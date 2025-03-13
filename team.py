import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import csv
from datetime import datetime

MAX_STUDENTS = 100
MAX_TEAMS = 20

class Student:
    def __init__(self, gender, phone, department, student_id, name, avg, score=None, team=None):
        self.gender = gender  # 성별
        self.phone = phone  # 전화번호
        self.department = department  # 학과
        self.student_id = student_id  # 학번
        self.name = name  # 이름
        self.avg = avg  # 평균 점수
        self.score = score if score is not None else avg  # 점수 (기본적으로 avg를 점수로 사용)
        self.team = team  # 팀 번호

def compare_score(student):
    return student  .score

def compare_team(student):
    return student.team

def load_csv():
    # CSV 파일을 선택하는 다이얼로그
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_dir.set(file_path)  # 선택한 파일 경로를 표시

def set_team_size():
    # 팀 사이즈를 설정하는 함수
    try:
        team_size.set(int(team_size_entry.get()))  # 입력값을 정수로 변환하여 저장
        print(f"팀 사이즈: {team_size.get()}")
        # 확인 버튼을 눌렀을 때 메시지 박스 표시
        messagebox.showinfo("확인", "팀 사이즈가 설정되었습니다.")  # 확인 메시지
    except ValueError:
        messagebox.showerror("입력 오류", "숫자를 입력하세요")  # 숫자가 아닌 값 입력 시 오류 메시지

def set_team_count():
    # 팀 개수를 설정하는 함수
    try:
        team_count.set(int(team_count_entry.get()))  # 입력값을 정수로 변환하여 저장
        print(f"팀 개수: {team_count.get()}")
        # 확인 버튼을 눌렀을 때 메시지 박스 표시
        messagebox.showinfo("확인", "팀 개수가 설정되었습니다.")  # 확인 메시지
    except ValueError:
        messagebox.showerror("입력 오류", "숫자를 입력하세요")  # 숫자가 아닌 값 입력 시 오류 메시지

def process_teams():
    # 팀 매칭 로직 수행 함수
    try:
        file_path = file_dir.get()
        if not file_path:
            raise ValueError("CSV 파일을 먼저 선택하세요")
        
        # CSV 파일 읽기 (인코딩을 지정해서 파일을 엽니다)
        students = []
        total_score = 0
        with open(file_path, 'r', encoding='utf-8') as file:  # 여기를 수정: CSV 파일을 utf-8로 읽음
            reader = csv.reader(file)
            next(reader)  # 첫 번째 행은 건너뜁니다 (헤더)
            for row in reader:
                if len(row) < 6:  # 각 행의 값이 6개보다 적으면 건너뜁니다.
                    continue  # 필요한 값이 아닌 경우 건너뛰기
                gender, phone, department, student_id, name, avg = row[:6]  # 첫 6개 항목만 사용
                avg = float(avg)  # 평균 점수는 실수로 변환
                # 실제 점수를 AVG로 설정, 없으면 기본 점수로 사용
                students.append(Student(gender, phone, department, student_id, name, avg))
                total_score += avg

        n = len(students)
        if n == 0:
            raise ValueError("학생 데이터가 없습니다.")
        
        average_score = total_score / n

        # 팀 개수 입력 확인
        team_count_value = team_count.get()
        if team_count_value <= 0 or team_count_value > n:
            raise ValueError("팀 개수는 1 이상, 학생 수 이하로 설정해야 합니다.")

        team_size_value = (n + team_count_value - 1) // team_count_value
        teams = [[] for _ in range(team_count_value)]
        team_scores = [0] * team_count_value
        team_sizes = [0] * team_count_value
        female_team_count = [0] * team_count_value  # 각 팀의 여성 학생 수를 추적

        # '핸디' 학생이 들어간 팀을 추적하기 위한 변수
        handy_assigned_teams = set()

        # 학생을 성별 및 평균 점수 순으로 정렬 (여성 먼저, 그다음 남성)
        students.sort(key=lambda x: (x.gender == 'M', x.score), reverse=True)

        # 팀 배치
        for student in students:
            if student.name == '핸디':
                # '핸디' 학생은 한 팀에 최대 1명만 배치
                assigned = False
                for i in range(team_count_value):
                    if i not in handy_assigned_teams:
                        teams[i].append(student)
                        team_scores[i] += student.score
                        team_sizes[i] += 1
                        handy_assigned_teams.add(i)  # 이 팀에는 '핸디' 학생이 배치됨
                        assigned = True
                        break
                if not assigned:
                    raise ValueError("핸디 학생이 배치될 수 없습니다. 팀이 부족합니다.")
            else:
                if student.gender == 'W':
                    # 여성 학생은 최대 2명까지 각 팀에 배치
                    min_index = min(range(team_count_value), key=lambda i: (team_sizes[i] == team_size_value, team_scores[i], female_team_count[i] >= 2))
                    female_team_count[min_index] += 1
                else:
                    # 남성 학생은 제한 없이 배치
                    min_index = min(range(team_count_value), key=lambda i: (team_sizes[i] == team_size_value, team_scores[i]))

                team_scores[min_index] += student.score
                teams[min_index].append(student)
                team_sizes[min_index] += 1

        # 결과 파일명에 날짜와 시간 포함
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"result_{current_time}.csv"

        # 결과를 CSV로 출력 (utf-8-sig 인코딩)
        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as file:  # utf-8-sig 인코딩 사용
            writer = csv.writer(file)
            writer.writerow(["Total students:", n])
            writer.writerow(["Average score:", f"{average_score:.2f}"])
            writer.writerow([])

            for i in range(team_count_value):
                writer.writerow([f"Team {i + 1}:"])
                for student in teams[i]:
                    writer.writerow([student.phone, student.department, student.student_id, student.name, student.avg, student.score])
                writer.writerow([f"Team average score: {team_scores[i] / team_sizes[i]:.2f}"])
                writer.writerow([])

        messagebox.showinfo("완료", f"결과가 {output_filename} 파일로 저장되었습니다.")

    except ValueError as e:
        messagebox.showerror("오류", str(e))  # 오류 메시지


# 메인 윈도우 생성
root = tk.Tk()
root.title("볼링 팀 매칭 프로그램")
root.geometry("500x350")

# 파일 경로를 저장할 변수
file_dir = tk.StringVar()

# 팀 인원수를 저장할 변수
team_size = tk.IntVar()

# 팀 개수를 저장할 변수
team_count = tk.IntVar()

# CSV 파일 불러오기 버튼
load_button = tk.Button(root, text="CSV 파일 불러오기", command=load_csv)
load_button.pack(pady=10)

# 파일 경로 표시 라벨
file_label = tk.Label(root, textvariable=file_dir, wraplength=400)
file_label.pack(pady=5)

# 팀 인원수 입력 필드
team_size_label = tk.Label(root, text="한 팀의 인원수 입력:")
team_size_label.pack(pady=5)

team_size_entry = tk.Entry(root)
team_size_entry.pack(pady=5)

# 확인 버튼 (팀 사이즈 설정)
confirm_button = tk.Button(root, text="팀 사이즈 확인", command=set_team_size)
confirm_button.pack(pady=5)

# 팀 개수 입력 필드
team_count_label = tk.Label(root, text="팀 개수 입력:")
team_count_label.pack(pady=5)

team_count_entry = tk.Entry(root)
team_count_entry.pack(pady=5)

# 확인 버튼 (팀 개수 설정)
confirm_team_count_button = tk.Button(root, text="팀 개수 확인", command=set_team_count)
confirm_team_count_button.pack(pady=5)

# 결과 처리 버튼
process_button = tk.Button(root, text="팀 매칭 처리", command=process_teams)
process_button.pack(pady=10)

# GUI 실행
root.mainloop()

