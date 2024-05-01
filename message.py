import socket
import select
import random
import ssl
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import certifi # type: ignore
import ssl

# Creating an SSL context using certifi's certificates to ensure secure connections.
context = ssl.create_default_context(cafile=certifi.where())
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def load_questions(filename):
    """Loads questions from a file, parsing questions and answers into a structured format."""
    questions = []
    with open(filename, 'r') as file:
        question = {}
        for line in file:
            # Start of a new question block
            if line.startswith('?'):
                # Save the previous question if it's complete
                if question:
                    if question.get('correct') is not None:
                        questions.append(question)
                    else:
                        print(f"Warning: Question without a correct answer not added: {question['question']}")
                question = {'question': line[1:].strip(), 'answers': [], 'correct': None}
            # Lines that start with '-' denote an incorrect answer
            elif line.startswith('-'):
                question['answers'].append(line[1:].strip())
            # Lines that start with '+' denote the correct answer
            elif line.startswith('+'):
                answer = line[1:].strip()
                question['answers'].append(answer)
                question['correct'] = len(question['answers']) - 1
        # Check and add the last question
        if question and question.get('correct') is not None:
            questions.append(question)
        elif question:
            print(f"Warning: Question without a correct answer not added: {question['question']}")
    return questions

def send_question(conn, question):
    """Sends a question and its possible answers over a network connection."""
    options = question['answers']
    conn.sendall(f"{question['question']}\n".encode())
    for i, option in enumerate(options):
        conn.sendall(f"{chr(65+i)}. {option}\n".encode())
    conn.sendall(b"Your answer (A, B, C, etc.): ")

def receive_answer(conn):
    """Receives a user's answer from the network connection."""
    ready = select.select([conn], [], [])
    if ready[0]:
        answer = conn.recv(1024).decode().strip().upper()
        return answer, True
    return None, False

def evaluate_answer(conn, answer, correct_answer):
    """Evaluates the user's answer and sends feedback."""
    if answer == chr(65 + correct_answer):
        conn.sendall(b"Correct!\n")
        return True
    else:
        conn.sendall(f"Wrong! The correct answer was {chr(65 + correct_answer)}\n".encode())
        return False

def send_email_manual(score, total_questions, recipient_email):
    """Sends an email manually via SMTP to provide test results."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 465  # Gmail's SMTP server uses port 465 for SSL
    sender_email = "u21447412@tuks.co.za"  # Your Gmail address
    sender_password = "dtxa emmo aflj kwbo"  # Your Gmail App Password

    # SSL context for secure email connection
    context = ssl.create_default_context(cafile=certifi.where())
    with socket.create_connection((smtp_server, smtp_port)) as sock:
        with context.wrap_socket(sock, server_hostname=smtp_server) as server:
            print(server.recv(1024).decode())  # Initial greeting
            server.send(b'EHLO gmail.com\r\n')
            print(server.recv(1024).decode())  # EHLO response

            # Base64 encode user and password, then authenticate
            auth_login = base64.b64encode(f"{sender_email}".encode()).decode()
            auth_password = base64.b64encode(f"{sender_password}".encode()).decode()
            server.send(b'AUTH LOGIN\r\n')
            print(server.recv(1024).decode())
            server.send(f"{auth_login}\r\n".encode())
            print(server.recv(1024).decode())
            server.send(f"{auth_password}\r\n".encode())
            print(server.recv(1024).decode())

            # Sending MAIL FROM and RCPT TO commands
            server.send(f'MAIL FROM: <{sender_email}>\r\n'.encode())
            print(server.recv(1024).decode())
            server.send(f'RCPT TO: <{recipient_email}>\r\n'.encode())
            print(server.recv(1024).decode())

            # Start sending email data
            server.send(b'DATA\r\n')
            print(server.recv(1024).decode())
            subject = "Test Results"
            content = f"Your score is {score}/{total_questions}."
            header = f"From: {sender_email}\r\nTo: {recipient_email}\r\nSubject: {subject}\r\n"
            message = f"{header}\r\n{content}\r\n.\r\n"
            server.send(message.encode())
            print(server.recv(1024).decode())

            server.send(b'QUIT\r\n')
            print(server.recv(1024).decode())  # Confirmation of quit

def run_server(questions, port=55556):
    """Sets up a server to interact with clients, handle questions and results."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen()
        print(f"Server listening on port {port}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            score = 0
            total_questions = 0

            random.shuffle(questions)  # Randomize the order of questions

            for question in questions:
                send_question(conn, question)
                answer, received = receive_answer(conn)

                if not received:
                    continue

                if evaluate_answer(conn, answer, question['correct']):
                    score += 1
                total_questions += 1

                conn.sendall(b"Continue? (Y/N): ")
                if conn.recv(1024).decode().strip().upper() != 'Y':
                    break

            conn.sendall(f"Your score: {score}/{total_questions}\n".encode())
            conn.sendall(b"Enter your email to receive the results: ")
            email = conn.recv(1024).decode().strip()
            send_email_manual(score, total_questions, email)
            conn.sendall(b"Results emailed successfully!\n")

if __name__ == "__main__":
    questions = load_questions("Prac 6/questions.txt")
    run_server(questions)
