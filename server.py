# app.py (Flask 서버 코드)

from flask import Flask, render_template_string, request, jsonify
import socket
import threading

app = Flask(__name__)

# 타겟 컴퓨터와 연결할 소켓
client_socket = None

# 타겟 컴퓨터와 연결
def connect_to_target():
    global client_socket
    try:
        # 타겟 컴퓨터 IP와 포트
        TARGET_IP = 'localhost'  # 타겟 컴퓨터의 IP 주소
        TARGET_PORT = 5001  # 타겟 컴퓨터 포트 (같은 포트로 설정)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((TARGET_IP, TARGET_PORT))
        print("타겟 컴퓨터와 연결됨")
    except Exception as e:
        print(f"타겟 컴퓨터 연결 실패: {e}")

# 명령어 전송 및 결과 받기
def send_command_to_target(command):
    global client_socket
    if client_socket:
        try:
            # 명령어 전송
            client_socket.send(command.encode('utf-8'))
            # 명령어 실행 결과 받기
            result = client_socket.recv(4096).decode('utf-8')
            return result
        except Exception as e:
            return f"오류 발생: {e}"
    return "타겟 컴퓨터와 연결되지 않았습니다."

# 웹 페이지 및 명령어 처리
@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form.get('command')
    if command:
        result = send_command_to_target(command)
        return render_template_string(open('index.html').read(), result=result)
    return render_template_string(open('index.html').read(), result="명령어를 입력해주세요.")

# 서버 실행
if __name__ == "__main__":
    # 타겟 컴퓨터 연결
    connect_to_target()
    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
