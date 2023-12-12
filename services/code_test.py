#%%
import contextlib
import io
import threading

## FIXME: timeout failed
class TimeoutException(Exception):
    pass

def pass_cases(user_code, test_cases):
    namespace = {}
    result = []

    # 使用 exec 執行用戶代碼
    output_stream = io.StringIO()
    error_stream = io.StringIO()
    try:
        exec(user_code, namespace, namespace)
    except Exception as e:
        return e

    def raise_timeout():
        raise TimeoutException("Execution timed out")

    for test_input, expected_output in test_cases:
        output_stream = io.StringIO()
        error_stream = io.StringIO()
        
        timer = threading.Timer(1, raise_timeout)
        timer.start()

        try:
            with contextlib.redirect_stdout(output_stream),\
                contextlib.redirect_stderr(error_stream):
                # 假設用戶定義的函數名為 fn
                actual_output = namespace['fn'](test_input)
            
            is_correct = "PASS" if actual_output == expected_output else "FAIL"
            error = error_stream.getvalue()
        except TimeoutException:
            actual_output = None
            is_correct = "TIMEOUT"
            print("Execution timed out")
        except Exception as e:
            actual_output = None
            is_correct = "ERROR"
            print(e)
        finally:
            timer.cancel()
        error = error_stream.getvalue()
        output = output_stream.getvalue()
        result.append((test_input, expected_output, actual_output, is_correct, output, error))

    answer = ""
    for test_input, expected_output, actual_output, is_correct, output, error in result:
        answer += f"[{is_correct}] Input: {test_input}\n \t Expected: {expected_output}, Actual: {actual_output}\n"
    return answer

# %%
# from cases.test1 import TestCase
# t = TestCase()
# user_code = '''
# def fn(x):
# 	if x in (1, 2):
# 		return 1
# 	return fn(x-1) + fn(x-2)
# '''
# ans = t.get_answers()

# pass_cases(user_code, ans)
# %%
