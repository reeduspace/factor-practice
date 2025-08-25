import random
import re
import streamlit as st

# ---------- ユーティリティ ----------
# 置き換え：パーサを「定数項なし=0」を許容する形に
FACTOR_PATTERN2 = re.compile(
    r"^\(\s*x\s*(?:([+\-]\s*\d+))?\s*\)\s*\(\s*x\s*(?:([+\-]\s*\d+))?\s*\)\s*$"
)

def parse_factor_input(s: str):
    """
    (x+a)(x+b) をパースして (a,b) を返す。
    a,b は整数。a/b を省略した場合は 0 とみなす。
    例: (x)(x-8) -> (0,-8),  (x+3)^2 -> (3,3)
    """
    s = s.strip().replace("*", "")
    # (x+3)^2 を (x+3)(x+3) として扱う
    if "^2" in s:
        s = re.sub(r"\(\s*x\s*([+\-]\s*\d+)\s*\)\s*\^\s*2",
                   r"(x\1)(x\1)", s)

    m = FACTOR_PATTERN2.match(s)
    if not m:
        return None
    def pick(g):
        return int(g.replace(" ", "")) if g else 0
    a = pick(m.group(1))
    b = pick(m.group(2))
    return a, b
def pretty_factor(p: int, q: int):
    def one(t):
        if t == 0:
            return "(x)"
        sign = "+" if t >= 0 else ""
        return f"(x{sign}{t})"
    # (x)(x) のときは (x)^2 と簡約表示
    if p == 0 and q == 0:
        return "(x)^2"
    return f"{one(p)}{one(q)}"

# ---------- 初期化 ----------
st.set_page_config(page_title="因数分解トレーニング（モニック）", page_icon="🧠", layout="centered")

if "problem" not in st.session_state:
    st.session_state.problem = None  # (b,c,p,q)
if "score" not in st.session_state:
    st.session_state.score = 0
if "combo" not in st.session_state:
    st.session_state.combo = 0
if "history" not in st.session_state:
    st.session_state.history = []  # [(question, user, correct, is_right)]

# ---------- 出題ロジック ----------
def new_problem():
    # p,q を -10..10 から生成（0も許す）。b=p+q, c=pq
    p = random.randint(-10, 10)
    q = random.randint(-10, 10)
    b = p + q
    c = p * q
    # 単純すぎる/面倒すぎる問題を軽くフィルタ
    if abs(b) > 14 or abs(c) > 40:
        return new_problem()
    st.session_state.problem = (b, c, *sorted((p, q)))

def ensure_problem():
    if st.session_state.problem is None:
        new_problem()

# ---------- UI ----------
st.title("因数分解トレーニング（x² + bx + c）")
st.caption("入力例：`(x+3)(x-2)` / `(x-2)(x+3)` / `(x+3)^2` もOK")

colA, colB, colC = st.columns(3)
with colA:
    if st.button("🔄 新しい問題", use_container_width=True):
        new_problem()
with colB:
    if st.button("🧹 リセット", use_container_width=True):
        st.session_state.score = 0
        st.session_state.combo = 0
        st.session_state.history.clear()
        st.session_state.problem = None
with colC:
    st.metric("Score", st.session_state.score)
    st.metric("Combo", st.session_state.combo)
def poly_latex(b: int, c: int):
    parts = [r"x^2"]
    if b != 0:
        parts.append(rf"{'+' if b>0 else '-'} {abs(b)}x")
    if c != 0:
        parts.append(rf"{'+' if c>0 else '-'} {abs(c)}")
    return " ".join(parts) if len(parts) > 1 else r"x^2"

# 出題表示のところを置き換え
st.subheader("問題")
st.latex(poly_latex(b, c))

ensure_problem()
b, c, p, q = st.session_state.problem
st.subheader("問題")
st.latex(poly_latex(b, c))

answer = st.text_input("因数分解の形を入力してください", key="answer_input", placeholder="(x+3)(x-2)")
submitted = st.button("✅ 判定する")

# ---------- 判定 ----------
if submitted:
    parsed = parse_factor_input(answer)
    if not parsed:
        st.error("入力の形式が違います。例：`(x+3)(x-2)`（空白OK、`*` は不要）")
    else:
        a, b_ = parsed
        user = tuple(sorted((a, b_)))
        correct = (p, q)
        is_right = user == correct
        st.session_state.history.append((f"x^2 + {b}x + {c}", pretty_factor(*user), pretty_factor(*correct), is_right))
        if is_right:
            st.success(f"正解！  正しい因数分解は **{pretty_factor(*correct)}**")
            st.session_state.score += 10
            st.session_state.combo += 1
            if st.session_state.combo in (5, 10, 20):
                st.balloons()
                st.info(f"{st.session_state.combo}コンボ！ いい流れ！")
            new_problem()  # 連続トレーニング
        else:
            st.error(f"不正解… 正しくは **{pretty_factor(*correct)}**")
            st.session_state.combo = 0  # コンボ途切れ

# ---------- ヒント ----------
with st.expander("🔎 ヒントを見る"):
    st.write("- 和が **b**, 積が **c** になる2数 **p, q** を探す")
    st.latex(rf"p+q={b},\quad pq={c}")
    st.write("- 二重根のときは `(x+{p})^2` の形でもOK")

# ---------- 履歴 ----------
st.subheader("履歴")
if not st.session_state.history:
    st.write("まだ履歴はありません。")
else:
    for i, (qtext, userf, corrf, ok) in enumerate(reversed(st.session_state.history[-10:]), 1):
        st.write(f"{i}. **{qtext}** → あなた：`{userf}` / 正解：`{corrf}`  {'✅' if ok else '❌'}")
