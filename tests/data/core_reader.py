subtitle_matcher_data = [
    # 자막과 번역의 시간이 일치
    (
        [
            {"time": 50, "subtitle": "what is your name?"},
            {"time": 56, "subtitle": "My name is John."},
            {"time": 70, "subtitle": "My name is Jane."},
        ],
        [
            {"time": 50, "subtitle": "이름이 뭐야?"},
            {"time": 56, "subtitle": "내 이름은 John이야"},
            {"time": 70, "subtitle": "내 이름은 Jane이야"},
        ],
        [
            {"time": 50, "subtitle": "what is your name?", "translation": "이름이 뭐야?"},
            {
                "time": 56,
                "subtitle": "My name is John.",
                "translation": "내 이름은 John이야",
            },
            {
                "time": 70,
                "subtitle": "My name is Jane.",
                "translation": "내 이름은 Jane이야",
            },
        ],
    ),
    # 자막 - 변역 - 자막 - 번역
    (
        [
            {"time": 50, "subtitle": "what is your name?"},
            {"time": 56, "subtitle": "My name is John."},
            {"time": 70, "subtitle": "My name is Jane."},
        ],
        [
            {"time": 52, "subtitle": "이름이 뭐야?"},
            {"time": 58, "subtitle": "내 이름은 John이야."},
            {"time": 72, "subtitle": "내 이름은 Jane이야."},
        ],
        [
            {"time": 50, "subtitle": "what is your name?", "translation": "이름이 뭐야?"},
            {
                "time": 56,
                "subtitle": "My name is John.",
                "translation": "내 이름은 John이야.",
            },
            {
                "time": 70,
                "subtitle": "My name is Jane.",
                "translation": "내 이름은 Jane이야.",
            },
        ],
    ),
    # 자막 - 번역 - 번역 - 자막
    (
        [
            {"time": 50, "subtitle": "what is your name?"},
            {"time": 56, "subtitle": "My name is John."},
            {"time": 70, "subtitle": "My name is Jane."},
        ],
        [
            {"time": 50, "subtitle": "이름이 뭐야?"},
            {"time": 52, "subtitle": "내 이름은 John이야."},
            {"time": 74, "subtitle": "내 이름은 Jane이야."},
        ],
        [
            {
                "time": 50,
                "subtitle": "what is your name?",
                "translation": "이름이 뭐야? 내 이름은 John이야.",
            },
            {"time": 56, "subtitle": "My name is John.", "translation": ""},
            {
                "time": 70,
                "subtitle": "My name is Jane.",
                "translation": "내 이름은 Jane이야.",
            },
        ],
    ),
    # 번역 - 자막 - 자막 - 번역
    (
        [
            {"time": 52, "subtitle": "what is your name?"},
            {"time": 54, "subtitle": "My name is John."},
            {"time": 70, "subtitle": "My name is Jane."},
        ],
        [
            {"time": 50, "subtitle": "이름이 뭐야?"},
            {"time": 56, "subtitle": "내 이름은 John이야."},
            {"time": 74, "subtitle": "내 이름은 Jane이야."},
        ],
        [
            {"time": 52, "subtitle": "what is your name?", "translation": "이름이 뭐야?"},
            {
                "time": 54,
                "subtitle": "My name is John.",
                "translation": "내 이름은 John이야.",
            },
            {
                "time": 70,
                "subtitle": "My name is Jane.",
                "translation": "내 이름은 Jane이야.",
            },
        ],
    ),
    # 번역 - 자막 - 번역 - 자막
    (
        [
            {"time": 52, "subtitle": "what is your name?"},
            {"time": 56, "subtitle": "My name is John."},
            {"time": 70, "subtitle": "My name is Jane."},
        ],
        [
            {"time": 50, "subtitle": "이름이 뭐야?"},
            {"time": 54, "subtitle": "내 이름은 John이야."},
            {"time": 74, "subtitle": "내 이름은 Jane이야."},
        ],
        [
            {
                "time": 52,
                "subtitle": "what is your name?",
                "translation": "이름이 뭐야? 내 이름은 John이야.",
            },
            {"time": 56, "subtitle": "My name is John.", "translation": ""},
            {
                "time": 70,
                "subtitle": "My name is Jane.",
                "translation": "내 이름은 Jane이야.",
            },
        ],
    ),
]
