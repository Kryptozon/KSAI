sessions = {}

def add_message(session_id, role, content):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": role, "content": content})
    if len(sessions[session_id]) > 20:
        sessions[session_id] = sessions[session_id][-20:]

def get_memory(session_id):
    return sessions.get(session_id, [])
