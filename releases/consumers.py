import json
import hashlib
import secrets
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


# ─── Adjective + Noun random username generator ──────────────────────────────

ADJECTIVES = [
    "cosmic", "dusty", "frozen", "hollow", "liquid", "neon", "rusty",
    "silent", "smoky", "wired", "broken", "chrome", "digital", "electric",
    "faded", "ghost", "glitch", "hyper", "indie", "jazzy", "kinetic",
    "lunar", "murky", "nocturnal", "orbital", "phantom", "quantum", "radical",
    "static", "turbo", "ultra", "vapor", "warped", "xenon", "yellow", "zero",
]

NOUNS = [
    "bass", "beat", "cipher", "crate", "deck", "drone", "echo", "fader",
    "flip", "freq", "gate", "grid", "groove", "house", "loop", "lyric",
    "mixer", "node", "pitch", "plug", "rack", "riff", "sample", "scratch",
    "signal", "slap", "snare", "static", "stomp", "synth", "tape", "track",
    "vinyl", "vox", "warp", "wave", "wire", "zone",
]


def generate_random_username():
    return f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}-{random.randint(10, 99)}"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hashed = stored_hash.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False


# ─── Canvas Consumer ──────────────────────────────────────────────────────────

class CanvasConsumer(AsyncWebsocketConsumer):
    GROUP = "wall_canvas"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

        # Send the current canvas state to the newly connected client
        canvas_data = await self.load_canvas()
        await self.send(text_data=json.dumps({
            "type": "canvas_init",
            "data": canvas_data,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def receive(self, text_data):
        msg = json.loads(text_data)
        action = msg.get("type")

        if action == "draw":
            # msg: { type, pixels: [{x, y, color}, ...] }
            pixels = msg.get("pixels", [])
            await self.save_pixels(pixels)
            await self.channel_layer.group_send(self.GROUP, {
                "type": "canvas_draw",
                "pixels": pixels,
            })

        elif action == "clear":
            await self.clear_canvas()
            await self.channel_layer.group_send(self.GROUP, {
                "type": "canvas_clear",
            })

    # Group message handlers
    async def canvas_draw(self, event):
        await self.send(text_data=json.dumps({
            "type": "draw",
            "pixels": event["pixels"],
        }))

    async def canvas_clear(self, event):
        await self.send(text_data=json.dumps({"type": "clear"}))

    # DB helpers
    @database_sync_to_async
    def load_canvas(self):
        from releases.models import WallCanvas
        instance = WallCanvas.get_instance()
        try:
            return json.loads(instance.canvas_data)
        except Exception:
            return {}

    @database_sync_to_async
    def save_pixels(self, pixels):
        from releases.models import WallCanvas
        instance = WallCanvas.get_instance()
        try:
            data = json.loads(instance.canvas_data)
        except Exception:
            data = {}
        for p in pixels:
            key = f"{p['x']},{p['y']}"
            if p.get("color") == "erase":
                data.pop(key, None)
            else:
                data[key] = p["color"]
        instance.canvas_data = json.dumps(data)
        instance.save()

    @database_sync_to_async
    def clear_canvas(self):
        from releases.models import WallCanvas
        instance = WallCanvas.get_instance()
        instance.canvas_data = '{}'
        instance.save()


# ─── Chat Consumer ────────────────────────────────────────────────────────────

class ChatConsumer(AsyncWebsocketConsumer):
    GROUP = "wall_chat"
    
    # Class-level dictionary to track presence: { channel_name: {"username": str, "offline": bool} }
    active_users = {}

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()
        # Immediately send the new user the current online list
        await self.send_presence_to_self()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)
        # If the user closes the tab, remove them from active tracking and tell everyone
        if self.channel_name in ChatConsumer.active_users:
            del ChatConsumer.active_users[self.channel_name]
            await self.broadcast_presence()

    async def receive(self, text_data):
        msg = json.loads(text_data)
        action = msg.get("type")

        if action == "chat_message":
            username = msg.get("username", "").strip()[:50]
            message = msg.get("message", "").strip()[:500]
            if not message:
                return

            # Save to DB
            await self.save_message(username, message)

            await self.channel_layer.group_send(self.GROUP, {
                "type": "chat_broadcast",
                "username": username,
                "message": message,
                "timestamp": timezone.now().strftime("%H:%M"),
            })
            
        elif action == "presence_update":
            username = msg.get("username", "").strip()[:50]
            offline = bool(msg.get("offline", False))
            
            if username:
                # Update their current connection state
                ChatConsumer.active_users[self.channel_name] = {
                    "username": username,
                    "offline": offline
                }
                # Tell the room about the change
                await self.broadcast_presence()

        elif action == "check_username":
            username = msg.get("username", "").strip()
            result = await self.check_username(username)
            await self.send(text_data=json.dumps({
                "type": "username_status",
                "username": username,
                **result,
            }))

        elif action == "reserve_username":
            username = msg.get("username", "").strip()[:50]
            password = msg.get("password", "")
            result = await self.reserve_username(username, password)
            await self.send(text_data=json.dumps({
                "type": "reserve_result",
                **result,
            }))

        elif action == "auth_username":
            username = msg.get("username", "").strip()[:50]
            password = msg.get("password", "")
            result = await self.auth_username(username, password)
            await self.send(text_data=json.dumps({
                "type": "auth_result",
                **result,
            }))

        elif action == "save_email":
            username = msg.get("username", "").strip()[:50]
            email = msg.get("email", "").strip()[:254]
            result = await self.save_email(username, email)
            await self.send(text_data=json.dumps({
                "type": "email_result",
                **result,
            }))

        elif action == "forgot_password":
            username = msg.get("username", "").strip()[:50]
            result = await self.send_reset_email(username)
            await self.send(text_data=json.dumps({
                "type": "forgot_password_result",
                **result,
            }))

    # ─── Group Handlers ───
    async def chat_broadcast(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "username": event["username"],
            "message": event["message"],
            "timestamp": event["timestamp"],
        }))
        
    async def presence_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "presence_list",
            "users": event["users"],
        }))

    # ─── Presence Helpers ───
    async def broadcast_presence(self):
        # Gather all unique usernames where offline is False
        visible_users = list(set([
            data["username"] for data in ChatConsumer.active_users.values() if not data.get("offline")
        ]))
        visible_users.sort(key=str.lower)
        
        await self.channel_layer.group_send(self.GROUP, {
            "type": "presence_list",
            "users": visible_users,
        })
        
    async def send_presence_to_self(self):
        # Used when a user first connects before they have set their own name
        visible_users = list(set([
            data["username"] for data in ChatConsumer.active_users.values() if not data.get("offline")
        ]))
        visible_users.sort(key=str.lower)
        
        await self.send(text_data=json.dumps({
            "type": "presence_list",
            "users": visible_users,
        }))

    # ─── DB Helpers ───
    @database_sync_to_async
    def save_message(self, username, message):
        from releases.models import ChatMessage
        ChatMessage.objects.create(username=username, message=message)

    @database_sync_to_async
    def check_username(self, username):
        from releases.models import ChatUsername
        try:
            entry = ChatUsername.objects.get(username__iexact=username)
            return {"taken": True, "password_protected": True, "has_email": bool(entry.email)}
        except ChatUsername.DoesNotExist:
            return {"taken": False, "password_protected": False, "has_email": False}

    @database_sync_to_async
    def reserve_username(self, username, password):
        from releases.models import ChatUsername
        if ChatUsername.objects.filter(username__iexact=username).exists():
            return {"success": False, "error": "Username already reserved."}
        if len(password) < 4:
            return {"success": False, "error": "Password must be at least 4 characters."}
        ChatUsername.objects.create(
            username=username,
            password_hash=hash_password(password),
        )
        return {"success": True}

    @database_sync_to_async
    def auth_username(self, username, password):
        from releases.models import ChatUsername
        try:
            entry = ChatUsername.objects.get(username__iexact=username)
            if verify_password(password, entry.password_hash):
                return {"success": True, "has_email": bool(entry.email)}
            return {"success": False, "error": "Wrong password."}
        except ChatUsername.DoesNotExist:
            return {"success": False, "error": "Username not found."}

    @database_sync_to_async
    def send_reset_email(self, username):
        from releases.models import ChatUsername, PasswordResetToken
        import secrets, os, resend
        generic = {"success": True, "message": "If that username has an email on file, a reset link has been sent."}
        try:
            entry = ChatUsername.objects.get(username__iexact=username)
        except ChatUsername.DoesNotExist:
            return generic
        if not entry.email:
            return generic
        PasswordResetToken.objects.filter(username=entry, used=False).update(used=True)
        token = secrets.token_urlsafe(48)
        PasswordResetToken.objects.create(username=entry, token=token)
        base_url = os.environ.get("SITE_URL", "https://fliphouserecords.com")
        reset_url = f"{base_url}/wall/reset-password/{token}/"
        resend.api_key = os.environ.get("RESEND_API_KEY", "")
        email_html = (
            "<div style='background:#000;color:#fff;font-family:Courier New,monospace;"
            "padding:40px;max-width:520px;margin:0 auto;border:1px solid rgba(255,255,255,0.2);border-radius:12px;'>"
            "<h1 style='font-size:1.4rem;letter-spacing:4px;margin-bottom:8px;'>FLIP HOUSE RECORDS</h1>"
            "<p style='color:rgba(255,255,255,0.4);font-size:0.8rem;letter-spacing:2px;margin-bottom:32px;'>"
            "// THE WALL - PASSWORD RESET //</p>"
            "<p style='color:rgba(255,255,255,0.85);line-height:1.7;margin-bottom:24px;'>"
            f"Someone requested a password reset for the username <strong style='color:#fff;'>{{}}</strong> on The Wall.<br><br>"
            "If this was you, click the button below. The link expires in <strong>1 hour</strong>.</p>"
            f"<a href='{reset_url}' style='display:inline-block;background:#fff;color:#000;text-decoration:none;"
            "padding:14px 28px;border-radius:8px;font-family:Courier New,monospace;font-size:0.9rem;"
            "letter-spacing:2px;margin-bottom:32px;'>RESET MY PASSWORD</a>"
            "<p style='color:rgba(255,255,255,0.3);font-size:0.75rem;line-height:1.6;'>"
            f"If you didn't request this, ignore this email - your password won't change.<br>"
            f"Link: {reset_url}</p></div>"
        ).format(entry.username)
        try:
            resend.Emails.send({
                "from": "Flip House Records <noreply@fliphouserecords.com>",
                "to": entry.email,
                "subject": "Reset your Wall password",
                "html": email_html,
            })
        except Exception:
            return {"success": False, "error": "Failed to send email. Try again later."}
        return generic

    @database_sync_to_async
    def save_email(self, username, email):
        from releases.models import ChatUsername
        import re
        # Basic email validation
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return {"success": False, "error": "Invalid email address."}
        try:
            entry = ChatUsername.objects.get(username__iexact=username)
            entry.email = email if email else None
            entry.save(update_fields=['email'])
            return {"success": True}
        except ChatUsername.DoesNotExist:
            return {"success": False, "error": "Username not found."}