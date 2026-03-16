"""
ReLoop Ultimate Chatbot API
Advanced NLP conversational assistant for sustainability guidance.

Features:
• Intent detection using fuzzy string matching
• Rich formatted responses
• Expandable knowledge base
• FAQ support
• Context-aware replies
• WebSocket real-time chat
"""

import json
import logging
from thefuzz import fuzz, process
from fastapi import APIRouter, WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chatbot"])

# Minimum similarity score (out of 100) required to trigger a match
SIMILARITY_THRESHOLD = 65

# ------------------------------------------------
# WASTE KNOWLEDGE BASE (Includes canonical phrases for matching)
# ------------------------------------------------

WASTE_KNOWLEDGE = {
    "plastic": {
        "phrases": ["plastic waste", "old plastic bottles", "plastic packaging", "polyethylene", "hdpe", "pvc", "recycle plastic"],
        "reuse": "Plastic waste can be recycled into containers, furniture, packaging, and textile fibers.",
        "industries": ["Plastic Recycling Plants", "Packaging Industry", "Textile Manufacturing"],
        "impact": "Recycling plastic saves up to 88% of energy compared to producing virgin plastic.",
        "tip": "♻️ Separate PET, HDPE, and PVC plastics to maximize recycling value.",
    },

    "metal": {
        "phrases": ["scrap metal", "steel offcuts", "aluminum cans", "copper wire", "iron scrap", "recycle steal", "recycle aluminium"],
        "reuse": "Metal scrap can be melted and reused indefinitely without losing quality.",
        "industries": ["Steel Recycling Plants", "Metal Foundries", "Construction Industry"],
        "impact": "Recycling steel saves around 60–74% energy compared to mining raw ore.",
        "tip": "🔩 Metals like aluminum and copper have extremely high recycling value.",
    },

    "wood": {
        "phrases": ["wood waste", "sawdust", "timber scraps", "old pallets", "lumber offcuts", "recycle wood"],
        "reuse": "Wood waste can be converted into biomass energy, particleboard, compost, or furniture.",
        "industries": ["Biomass Plants", "Furniture Manufacturing", "Paper Mills"],
        "impact": "Using wood waste for biomass reduces landfill methane emissions.",
        "tip": "🌳 Untreated wood waste is excellent for composting and bioenergy.",
    },

    "textile": {
        "phrases": ["textile waste", "old clothes", "fabric scraps", "clothing", "apparel waste", "recycle shirts"],
        "reuse": "Textile waste can be repurposed into insulation, cleaning cloths, and recycled fibers.",
        "industries": ["Insulation Manufacturing", "Second-hand Retail", "Industrial Cleaning"],
        "impact": "Recycling textiles saves water and reduces landfill waste from fast fashion.",
        "tip": "👕 Textile recycling prevents millions of tons of clothing from entering landfills.",
    },

    "food": {
        "phrases": ["food waste", "organic waste", "vegetable scraps", "spoiled food", "agricultural waste"],
        "reuse": "Organic food waste can be converted into biogas, fertilizer, or animal feed.",
        "industries": ["Biogas Plants", "Composting Facilities", "Animal Feed Processing"],
        "impact": "Biogas from food waste produces renewable energy while reducing methane emissions.",
        "tip": "🥗 Food waste is one of the best sources for renewable biogas energy.",
    },

    "glass": {
        "phrases": ["glass scrap", "broken glass", "glass bottles", "shattered windows", "recycle glass"],
        "reuse": "Glass can be recycled infinitely without losing purity or quality.",
        "industries": ["Glass Manufacturing", "Construction Aggregate", "Fiberglass Production"],
        "impact": "Using recycled glass reduces furnace energy consumption by up to 30%.",
        "tip": "🫙 Crushed recycled glass is called 'cullet' and reduces energy usage in glass furnaces.",
    },

    "paper": {
        "phrases": ["paper waste", "cardboard boxes", "shredded paper", "office paper", "cartons", "recycle cardboard"],
        "reuse": "Paper waste can be recycled into new packaging, cardboard, and insulation.",
        "industries": ["Paper Mills", "Packaging Companies", "Insulation Manufacturers"],
        "impact": "Recycling 1 ton of paper saves 17 trees and thousands of gallons of water.",
        "tip": "📄 Flatten cardboard boxes before recycling to save storage space.",
    },

    "electronic": {
        "phrases": ["electronic waste", "e-waste", "old computers", "broken circuit boards", "smartphones", "laptops"],
        "reuse": "E-waste contains valuable metals such as gold, silver, and copper that can be recovered.",
        "industries": ["E-waste Recycling Plants", "Metal Recovery Facilities", "Refurbishment Centers"],
        "impact": "Proper e-waste recycling prevents toxic chemicals from contaminating soil and water.",
        "tip": "💻 Only about 20% of global e-waste is recycled properly.",
    },

    "chemical": {
        "phrases": ["chemical waste", "solvents", "industrial chemicals", "hazardous liquids", "acetone"],
        "reuse": "Many chemical wastes can be purified and reused in industrial manufacturing processes.",
        "industries": ["Chemical Recycling Plants", "Solvent Recovery Facilities", "Hazardous Waste Treatment"],
        "impact": "Chemical recovery reduces environmental contamination risks.",
        "tip": "⚗️ Proper chemical waste treatment protects ecosystems and groundwater.",
    },

    "rubber": {
        "phrases": ["rubber waste", "old tires", "tyres", "shredded rubber", "vulcanized rubber", "recycle tires"],
        "reuse": "Rubber waste can be converted into asphalt materials, playground surfaces, or fuel through pyrolysis.",
        "industries": ["Tire Recycling Plants", "Asphalt Manufacturers", "Pyrolysis Plants"],
        "impact": "Recycling rubber reduces landfill fire risks and environmental pollution.",
        "tip": "🛞 Around 1 billion waste tires are generated globally every year.",
    },
}

# ------------------------------------------------
# FAQ RESPONSES (Includes canonical phrases for matching)
# ------------------------------------------------

FAQ_RESPONSES = {
    "what is reloop": {
        "phrases": ["what is reloop", "what does this platform do", "explain circular economy platform", "how does reloop work"],
        "response": "🔄 ReLoop is a circular economy platform connecting waste producers with industries that can reuse those materials."
    },
    "how to sell": {
        "phrases": ["how to sell", "how do i list waste", "where do i offer materials", "i want to sell scrap", "sell garbage"],
        "response": "📦 Steps to sell waste:\n1. Login/Register\n2. Go to Marketplace\n3. Create Listing\n4. Enter waste details\n5. AI suggests buyers"
    },
    "how to buy": {
        "phrases": ["how to buy", "how do i purchase", "i want to buy raw materials", "purchasing process", "purchase waste"],
        "response": "🛒 Steps to buy waste materials:\n1. Open Marketplace\n2. Search or filter materials\n3. Select listing\n4. Click 'Buy'"
    },
    "circular economy": {
        "phrases": ["what is circular economy", "explain sustainability", "why recycle"],
        "response": "🌍 Circular economy keeps resources in use as long as possible by recycling and reusing materials, preventing landfill waste."
    },
    "impact": {
        "phrases": ["what is the environmental impact", "how are co2 savings calculated", "impact score"],
        "response": "🌱 ReLoop calculates environmental benefits like CO₂ saved, energy saved, and landfill reduction based on the volume and type of material exchanged."
    },
    "help": {
        "phrases": ["help me", "what can you do", "what are your features", "capabilities"],
        "response": "💡 Ask me about:\n• Recycling materials (plastic, metal, wood)\n• Platform usage (how to sell, how to buy)\n• Sustainability concepts\n• Environmental impact"
    },
}

# ------------------------------------------------
# INTENT DETECTION
# ------------------------------------------------

def detect_intent(message: str):
    """Detect intent using fuzzy semantic similarity matching."""
    
    best_match = None
    best_score = 0
    match_type = None

    # Check against material categories
    for material, cat in WASTE_KNOWLEDGE.items():
        # Get the best matching phrase for this category
        match_result = process.extractOne(message.lower(), cat["phrases"], scorer=fuzz.token_set_ratio)
        if match_result:
            phrase, score = match_result[0], match_result[1]
            if score > best_score:
                best_score = score
                best_match = material
                match_type = "material"

    # Check against FAQs
    for faq_key, faq in FAQ_RESPONSES.items():
        match_result = process.extractOne(message.lower(), faq["phrases"], scorer=fuzz.token_set_ratio)
        if match_result:
            phrase, score = match_result[0], match_result[1]
            if score > best_score:
                best_score = score
                best_match = faq_key
                match_type = "faq"

    if best_score >= SIMILARITY_THRESHOLD:
        logger.info(f"Matched '{message}' to {match_type}:{best_match} with score {best_score}")
        return match_type, best_match
    
    logger.info(f"No strong match for '{message}'. Best score was {best_score} for {best_match}")
    return None, None


# ------------------------------------------------
# RESPONSE GENERATOR
# ------------------------------------------------

def generate_material_response(material):
    info = WASTE_KNOWLEDGE.get(material)
    if not info:
        return "I couldn't find information for that material."
    return (
        f"♻️ **{material.title()} Waste Guide**\n\n"
        f"📋 Reuse Information:\n{info['reuse']}\n\n"
        f"🏭 Suitable Industries:\n"
        f"{', '.join(info['industries'])}\n\n"
        f"🌍 Environmental Impact:\n{info['impact']}\n\n"
        f"💡 Tip:\n{info['tip']}\n\n"
        f"You can create a listing for this material in the Marketplace!"
    )


def chatbot_reply(message):
    message = message.strip()
    if not message:
        return "Please ask me a question!"

    # Process common greetings directly for speed
    msg_lower = message.lower()
    if fuzz.ratio(msg_lower, "hello") > 80 or fuzz.ratio(msg_lower, "hi") > 80 or fuzz.partial_ratio(msg_lower, "hi there") > 80 or fuzz.partial_ratio(msg_lower, "hey") > 80:
        return (
            "👋 Hello! I'm the ReLoop Sustainability Assistant.\n\n"
            "Ask me about recycling materials, platform usage, or sustainability topics."
        )

    if fuzz.partial_ratio(msg_lower, "thank") > 80:
        return "😊 You're welcome! Happy to help build a circular economy."

    # NLP Intent Detection
    match_type, match_key = detect_intent(message)

    if match_type == "faq":
        return FAQ_RESPONSES[match_key]["response"]
    elif match_type == "material":
        return generate_material_response(match_key)

    # Fallback for low confidence
    return (
        "🤔 I'm not entirely sure I understand. Could you rephrase?\n\n"
        "Try asking about specific materials (e.g., 'who buys old tires?', 'scrap metal recycling')\n"
        "or platform usage (e.g., 'how do I sell waste?')."
    )


# ------------------------------------------------
# WEBSOCKET CONNECTION MANAGER
# ------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: str, sender: str = "user"):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(json.dumps({
                    "sender": sender,
                    "message": message,
                    "room_id": room_id
                }))

manager = ConnectionManager()

# ------------------------------------------------
# WEBSOCKET ENDPOINT
# ------------------------------------------------
from app.database import SessionLocal
from app.models.buy_request import BuyRequest
from app.models.user import User
from app.security.auth import decode_access_token

@router.websocket("/ws/chat")
async def chatbot_websocket(websocket: WebSocket, room_id: str = "bot", token: str = None):
    # Security Rule: Identify room privileges if not a bot room
    if room_id.startswith("chat_"):
        request_id = room_id.replace("chat_", "")
        if not request_id.isdigit():
            await websocket.close(code=1008, reason="Invalid chat room")
            return
            
        if not token:
            await websocket.close(code=1008, reason="Unauthorized: Missing token")
            return
            
        db = SessionLocal()
        try:
            payload = decode_access_token(token)
            username = payload.get("sub")
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise Exception("User not found")
            user_id = user.id
        except Exception as e:
            db.close()
            await websocket.close(code=1008, reason=f"Unauthorized: Invalid token {e}")
            return
            
        req = db.query(BuyRequest).filter(BuyRequest.id == int(request_id)).first()
        db.close()
        
        if not req:
            await websocket.close(code=1008, reason="Buy Request not found")
            return
            
        if user_id not in [req.buyer_id, req.seller_id]:
            await websocket.close(code=1008, reason="Unauthorized: Not a participant in this request")
            return

    await manager.connect(websocket, room_id)

    try:
        if room_id == "bot":
            await websocket.send_text(json.dumps({
                "sender": "bot",
                "message":
                "👋 Welcome to ReLoop! I'm your advanced sustainability assistant.\n"
                "Ask me questions naturally like 'what should I do with old cardboard?' or 'how do I sell scrap metal?'."
            }))
        else:
            await manager.broadcast(f"--- User joined room: {room_id} ---", room_id, sender="system")

        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_message = payload.get("message", "")
                user_sender = payload.get("sender", "user")
            except:
                user_message = data
                user_sender = "user"

            if room_id == "bot":
                # Get semantic response
                response = chatbot_reply(user_message)
                await websocket.send_text(json.dumps({
                    "sender": "bot",
                    "message": response
                }))
            else:
                # E2EE Peer-to-peer broadcast & persistence
                # Only save if sender is not 'system'
                if user_sender != "system":
                    from app.models.chat_message import ChatMessage
                    db = SessionLocal()
                    new_msg = ChatMessage(
                        room_id=room_id,
                        sender_id=user_id, # user_id is set above via token
                        encrypted_message=user_message
                    )
                    db.add(new_msg)
                    db.commit()
                    db.close()

                await manager.broadcast(user_message, room_id, sender=user_sender)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        if room_id != "bot":
            await manager.broadcast("--- User left the room ---", room_id, sender="system")
        logger.info(f"User disconnected from room {room_id}")

