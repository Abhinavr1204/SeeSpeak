# backend/memory.py

conversation = []

def add_memory(user, ai):
    conversation.append({"user": user, "ai": ai})

    if len(conversation) > 10:
        conversation.pop(0)

def get_memory():
    return conversation