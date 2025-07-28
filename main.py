
import streamlit as st
import random
from sympy import symbols, Eq, expand, simplify

x = symbols('x')

def generate_problem():
    r1 = random.randint(-9, 9)
    r2 = random.randint(-9, 9)
    while r1 == 0 or r2 == 0:
        r1 = random.randint(-9, 9)
        r2 = random.randint(-9, 9)
    expr = expand((x + r1) * (x + r2))
    return expr, r1, r2

st.title("因数分解100本ノック！ (normal版)")
st.write("表示された式を因数分解しよう！ 例: (x+2)(x-3)")

if 'expr' not in st.session_state:
    st.session_state.expr, st.session_state.r1, st.session_state.r2 = generate_problem()

st.latex(f"{st.session_state.expr}")

user_answer = st.text_input("因数分解の答えを入力：（例）(x+2)(x-3)")

if st.button("答え合わせ"):
    try:
        user_expr = simplify(user_answer.replace(" ", "").replace("X", "x"))
        correct_expr = simplify((x + st.session_state.r1) * (x + st.session_state.r2))
        if user_expr == correct_expr:
            st.success("正解！すごーい！🎉")
        else:
            sorted_r = sorted([st.session_state.r1, st.session_state.r2])
            st.error(f"残念、不正解！ 正解は (x{sorted_r[0]:+})(x{sorted_r[1]:+})")
    except Exception as e:
        st.error(f"エラー：入力の形式を見直してみてね（例：(x+1)(x-2)）")

if st.button("次の問題へ"):
    st.session_state.expr, st.session_state.r1, st.session_state.r2 = generate_problem()
    st.experimental_rerun()
