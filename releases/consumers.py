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

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

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

    async def chat_broadcast(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "username": event["username"],
            "message": event["message"],
            "timestamp": event["timestamp"],
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        from releases.models import ChatMessage
        ChatMessage.objects.create(username=username, message=message)

    @database_sync_to_async
    def check_username(self, username):
        from releases.models import ChatUsername
        try:
            entry = ChatUsername.objects.get(username__iexact=username)
            return {"taken": True, "password_protected": True}
        except ChatUsername.DoesNotExist:
            return {"taken": False, "password_protected": False}

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
                return {"success": True}
            return {"success": False, "error": "Wrong password."}
        except ChatUsername.DoesNotExist:
            return {"success": False, "error": "Username not found."}