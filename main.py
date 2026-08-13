import json
import time


EPSILON = 1e-9
BENCHMARK_REPEAT = 10


def normalize_label(label):
    """JSON의 여러 라벨 표현을 Cross 또는 X로 통일한다."""
    if not isinstance(label, str):
        return None

    normalized = label.strip().lower()
    if normalized == "+" or normalized == "cross":
        return "Cross"
    if normalized == "x":
        return "X"
    return None


def validate_matrix(matrix, size):
    """matrix가 숫자로 이루어진 size x size 배열인지 확인한다."""
    if not isinstance(matrix, list) or len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            return False
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
    return True


def mac(pattern, filter_matrix):
    """두 N x N 행렬에서 같은 위치의 값을 곱해 모두 더한다."""
    size = len(pattern)
    score = 0.0

    for i in range(size):
        for j in range(size):
            score += pattern[i][j] * filter_matrix[i][j]

    return score


def flatten_matrix(matrix):
    """2차원 행렬의 값을 행 순서대로 1차원 리스트에 담는다."""
    flat_values = []
    for row in matrix:
        for value in row:
            flat_values.append(value)
    return flat_values


def mac_1d(pattern, filter_values):
    """두 1차원 리스트에서 같은 위치의 값을 곱해 모두 더한다."""
    score = 0.0
    for i in range(len(pattern)):
        score += pattern[i] * filter_values[i]
    return score


def generate_cross_pattern(size):
    """가운데 행과 열이 1인 홀수 크기의 Cross 패턴을 만든다."""
    pattern = []
    middle = size // 2
    for row in range(size):
        pattern_row = []
        for column in range(size):
            if row == middle or column == middle:
                pattern_row.append(1.0)
            else:
                pattern_row.append(0.0)
        pattern.append(pattern_row)
    return pattern


def generate_x_pattern(size):
    """두 대각선이 1인 X 패턴을 만든다."""
    pattern = []
    for row in range(size):
        pattern_row = []
        for column in range(size):
            if row == column or row + column == size - 1:
                pattern_row.append(1.0)
            else:
                pattern_row.append(0.0)
        pattern.append(pattern_row)
    return pattern


def compare_scores(cross_score, x_score):
    """epsilon을 적용해 두 점수의 판정을 반환한다."""
    if abs(cross_score - x_score) < EPSILON:
        return "UNDECIDED"
    if cross_score > x_score:
        return "Cross"
    return "X"


def input_matrix(name, size=3):
    """사용자에게 숫자 행렬을 한 줄씩 입력받는다."""
    print("\n" + name + "을(를) 입력하세요.")
    matrix = []

    for row_number in range(1, size + 1):
        while True:
            row_text = input(str(row_number) + "행: ")
            values = row_text.split()

            if len(values) != size:
                print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
                continue

            try:
                row = [float(value) for value in values]
            except ValueError:
                print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
                continue

            matrix.append(row)
            break

    return matrix


def benchmark_mac(pattern, filter_matrix, repeat=BENCHMARK_REPEAT):
    """mac 함수 호출 구간만 반복 측정해 평균 밀리초를 구한다."""
    start_time = time.perf_counter()
    for _ in range(repeat):
        mac(pattern, filter_matrix)
    end_time = time.perf_counter()

    average_seconds = (end_time - start_time) / repeat
    return average_seconds * 1000.0


def benchmark_mac_1d(pattern, filter_values, repeat=BENCHMARK_REPEAT):
    """mac_1d 함수 호출 구간만 반복 측정해 평균 밀리초를 구한다."""
    start_time = time.perf_counter()
    for _ in range(repeat):
        mac_1d(pattern, filter_values)
    end_time = time.perf_counter()

    average_seconds = (end_time - start_time) / repeat
    return average_seconds * 1000.0


def run_manual_mode():
    """3 x 3 필터 두 개와 패턴을 입력받아 판정한다."""
    filter_a = input_matrix("3x3 필터 A")
    filter_b = input_matrix("3x3 필터 B")
    print("\n필터 A, B 저장 완료")
    pattern = input_matrix("3x3 패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    average_ms = benchmark_mac(pattern, filter_b)

    if abs(score_a - score_b) < EPSILON:
        decision = "UNDECIDED"
    elif score_a > score_b:
        decision = "A"
    else:
        decision = "B"

    print("\n=== 판정 결과 ===")
    print("필터 A MAC 점수:", format_score(score_a))
    print("필터 B MAC 점수:", format_score(score_b))
    print(
        "연산 시간(평균/" + str(BENCHMARK_REPEAT) + "회):",
        format(average_ms, ".6f"),
        "ms"
    )
    print("판정:", decision)


def load_json_data(filename="data.json"):
    """UTF-8 JSON 파일을 읽고 파이썬 객체로 반환한다."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("오류: " + filename + " 파일을 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError as error:
        print("오류: 올바른 JSON 형식이 아닙니다. (" + str(error) + ")")
        return None
    except UnicodeError as error:
        print("오류: JSON 파일의 문자 인코딩을 읽을 수 없습니다. (" + str(error) + ")")
        return None
    except OSError as error:
        print("오류: JSON 파일을 읽을 수 없습니다. (" + str(error) + ")")
        return None

    if not isinstance(data, dict):
        print("오류: JSON의 최상위 값은 객체여야 합니다.")
        return None
    return data


def get_pattern_size(pattern_key):
    """size_13_2와 같은 키에서 13을 꺼낸다."""
    if not isinstance(pattern_key, str):
        return None

    parts = pattern_key.split("_")
    if len(parts) != 3 or parts[0] != "size":
        return None

    try:
        size = int(parts[1])
        case_number = int(parts[2])
    except ValueError:
        return None

    if size <= 0 or case_number <= 0:
        return None
    return size


def format_score(score):
    """점수를 읽기 쉬우면서도 충분한 정밀도로 표시한다."""
    return format(score, ".12g")


def get_filter_matrices(filter_group):
    """필터 이름을 정규화해 Cross 필터와 X 필터를 찾는다."""
    if not isinstance(filter_group, dict):
        return None, None

    cross_filter = None
    x_filter = None
    for filter_name, filter_matrix in filter_group.items():
        normalized_name = normalize_label(filter_name)
        if normalized_name == "Cross":
            cross_filter = filter_matrix
        elif normalized_name == "X":
            x_filter = filter_matrix

    return cross_filter, x_filter


def print_case_result(case_name, cross_score, x_score, decision,
                      expected_label, passed, reason=None):
    """JSON 케이스 하나의 분석 결과를 정해진 형식으로 출력한다."""
    print("\n--- " + str(case_name) + " ---")
    if cross_score is not None:
        print("Cross 점수:", format_score(cross_score))
    if x_score is not None:
        print("X 점수:", format_score(x_score))
    if decision is not None:
        print("판정:", decision)
    if expected_label is not None:
        print("expected:", expected_label)
    print("결과:", "PASS" if passed else "FAIL")
    if reason is not None:
        print("사유:", reason)


def analyze_case(case_name, case_data, filters):
    """한 JSON 패턴을 검증하고 점수, 판정, 성공 여부를 반환한다."""
    size = get_pattern_size(case_name)
    if size is None:
        return None, None, None, None, False, "pattern key 형식 오류"

    if not isinstance(case_data, dict):
        return None, None, None, None, False, "패턴 데이터 형식 오류"
    if "input" not in case_data:
        return None, None, None, None, False, "input 값 누락"
    if "expected" not in case_data:
        return None, None, None, None, False, "expected 값 누락"

    pattern = case_data["input"]
    expected_label = normalize_label(case_data["expected"])
    if expected_label is None:
        return None, None, None, str(case_data["expected"]), False, "알 수 없는 라벨"
    if not validate_matrix(pattern, size):
        return None, None, None, expected_label, False, "패턴 크기 불일치"

    filter_key = "size_" + str(size)
    if not isinstance(filters, dict) or filter_key not in filters:
        return None, None, None, expected_label, False, "해당 크기의 필터 없음"

    filter_group = filters[filter_key]
    if not isinstance(filter_group, dict):
        return None, None, None, expected_label, False, "필터 데이터 형식 오류"
    cross_filter, x_filter = get_filter_matrices(filter_group)
    if cross_filter is None or x_filter is None:
        return None, None, None, expected_label, False, "필요한 필터 누락"

    if not validate_matrix(cross_filter, size) or not validate_matrix(x_filter, size):
        return None, None, None, expected_label, False, "필터 크기 불일치"

    cross_score = mac(pattern, cross_filter)
    x_score = mac(pattern, x_filter)
    decision = compare_scores(cross_score, x_score)
    passed = decision == expected_label

    if passed:
        reason = None
    elif decision == "UNDECIDED":
        reason = "epsilon 기준 동점"
    else:
        reason = "판정과 expected 불일치"

    return cross_score, x_score, decision, expected_label, passed, reason


def find_benchmark_matrices(data, size):
    """성능 측정에 쓸 같은 크기의 유효한 패턴과 필터를 찾는다."""
    if size == 3:
        pattern = generate_x_pattern(3)
        filter_matrix = generate_x_pattern(3)
        return pattern, filter_matrix

    filters = data.get("filters")
    patterns = data.get("patterns")
    filter_key = "size_" + str(size)

    if not isinstance(filters, dict) or filter_key not in filters:
        return None, None
    filter_group = filters[filter_key]
    filter_matrix, unused_x_filter = get_filter_matrices(filter_group)
    if filter_matrix is None:
        return None, None
    if not validate_matrix(filter_matrix, size):
        return None, None

    if not isinstance(patterns, dict):
        return None, None
    for case_name, case_data in patterns.items():
        if get_pattern_size(case_name) == size and isinstance(case_data, dict):
            pattern = case_data.get("input")
            if validate_matrix(pattern, size):
                return pattern, filter_matrix

    return None, None


def print_performance_results(data):
    """같은 데이터로 2D와 1D MAC의 평균 실행 시간을 비교한다."""
    print("\n=== 2D / 1D MAC 성능 비교 ===")
    print("크기 / 2D 평균(ms) / 1D 평균(ms) / 연산 횟수(N²)")
    performance_results = []

    for size in [3, 5, 13, 25]:
        pattern, filter_matrix = find_benchmark_matrices(data, size)
        if pattern is None or filter_matrix is None:
            print(
                str(size) + "x" + str(size)
                + " / 측정 불가 / 측정 불가 / " + str(size * size)
            )
            continue

        flat_pattern = flatten_matrix(pattern)
        flat_filter = flatten_matrix(filter_matrix)
        score_2d = mac(pattern, filter_matrix)
        score_1d = mac_1d(flat_pattern, flat_filter)
        if abs(score_2d - score_1d) >= EPSILON:
            print(str(size) + "x" + str(size) + " / 2D와 1D 점수 불일치")
            continue

        average_2d_ms = benchmark_mac(pattern, filter_matrix)
        average_1d_ms = benchmark_mac_1d(flat_pattern, flat_filter)
        performance_results.append((size, average_2d_ms, average_1d_ms))
        print(
            str(size) + "x" + str(size)
            + " / " + format(average_2d_ms, ".6f") + " ms"
            + " / " + format(average_1d_ms, ".6f") + " ms"
            + " / " + str(size * size)
        )

    return performance_results


def run_json_mode():
    """data.json의 모든 패턴을 분석하고 결과와 성능을 요약한다."""
    data = load_json_data()
    if data is None:
        return

    filters = data.get("filters")
    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        print("오류: patterns 데이터가 없거나 객체 형식이 아닙니다.")
        return

    total_count = 0
    passed_count = 0
    failed_cases = []

    print("\n=== data.json 분석 ===")
    for case_name, case_data in patterns.items():
        total_count += 1
        result = analyze_case(case_name, case_data, filters)
        cross_score, x_score, decision, expected_label, passed, reason = result

        print_case_result(
            case_name,
            cross_score,
            x_score,
            decision,
            expected_label,
            passed,
            reason
        )

        if passed:
            passed_count += 1
        else:
            failed_cases.append((str(case_name), reason))

    print_performance_results(data)

    print("\n=== 결과 요약 ===")
    print("총 테스트:", total_count, "개")
    print("통과:", passed_count, "개")
    print("실패:", total_count - passed_count, "개")

    if failed_cases:
        print("\n실패 케이스:")
        for case_name, reason in failed_cases:
            print("- " + case_name + ": " + reason)


def select_mode():
    """올바른 메뉴 번호가 들어올 때까지 다시 입력받는다."""
    while True:
        print("=== Mini NPU Simulator ===")
        print("\n[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        choice = input("선택: ").strip()

        if choice == "1" or choice == "2":
            return choice
        print("잘못된 선택입니다. 1 또는 2를 입력하세요.\n")


def main():
    choice = select_mode()
    if choice == "1":
        run_manual_mode()
    else:
        run_json_mode()


if __name__ == "__main__":
    main()
