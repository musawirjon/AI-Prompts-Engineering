from flask import jsonify
import duckdb
import json

class ChatModel():
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = duckdb.connect('chat_history.db', read_only=False, allow_concurrent_connections=True)
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def __del__(self):
        if self.conn:
            self.conn.close()

    def dictionary_store(self, message):
        if 'content' in message:
            message['content'] = message['content'] + "\n"
        
        # Insert the message into DuckDB
        self.conn.execute("""
            INSERT INTO qa (role, content)
            VALUES (?, ?)
        """, [message.get('role'), message.get('content')])
        
        self.conn.commit()
    
    def get_conversation(self):
        # Retrieve all messages from the database
        result = self.conn.execute("""
            SELECT role, content 
            FROM qa 
            ORDER BY timestamp ASC
        """).fetchall()
        
        # Convert to list of dictionaries format
        conversation = []
        for row in result:
            conversation.append({
                'role': row[0],
                'content': row[1]
            })
            
        return conversation