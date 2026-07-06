import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse

PORT = 8080
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "odds_history.db")

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Fetch latest snapshot for each match
                cursor.execute('''
                    SELECT match_name, timestamp, jc_odds, pin_odds, best_ev, best_selection
                    FROM odds_history
                    WHERE id IN (
                        SELECT MAX(id)
                        FROM odds_history
                        GROUP BY match_name
                    )
                    ORDER BY timestamp DESC
                ''')
                
                rows = cursor.fetchall()
                data = []
                for r in rows:
                    match_name = r[0]
                    # Fetch the last 15 EV values and timestamps for the line chart
                    cursor.execute('''
                        SELECT timestamp, best_ev FROM odds_history
                        WHERE match_name = ?
                        ORDER BY timestamp DESC LIMIT 15
                    ''', (match_name,))
                    history = cursor.fetchall()
                    history.reverse()
                    
                    timestamps = [h[0] for h in history]
                    evs = [h[1] for h in history]
                    
                    data.append({
                        "match_name": match_name,
                        "timestamp": r[1],
                        "jc_odds": json.loads(r[2]),
                        "pin_odds": json.loads(r[3]),
                        "best_ev": r[4],
                        "best_selection": r[5],
                        "chart_times": timestamps,
                        "chart_evs": evs
                    })
                
                conn.close()
                self.wfile.write(json.dumps(data).encode())
                
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            # Serve index.html or other static files
            super().do_GET()

if __name__ == "__main__":
    Handler = DashboardHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"📊 Quant-JingCai Dashboard running at http://localhost:{PORT}")
        httpd.serve_forever()
