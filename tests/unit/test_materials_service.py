import pytest
from app.services.materials import extract_items_from_ocr


@pytest.mark.asyncio
def test_extract_items_from_ocr():
    json_data = {
        "ParsedResults": [
            {
                "Overlay": {
                    "Lines": [
                        {
                            "LineText": "으팝페이",
                            "Words": [
                                {
                                    "WordText": "으팝페이",
                                    "Left": 148,
                                    "Top": 134,
                                    "Height": 20,
                                    "Width": 98,
                                }
                            ],
                            "MaxHeight": 20,
                            "MinTop": 134,
                        },
                        {
                            "LineText": "www.phampay.co.kr",
                            "Words": [
                                {
                                    "WordText": "www.phampay.co.kr",
                                    "Left": 146,
                                    "Top": 152,
                                    "Height": 12,
                                    "Width": 106,
                                }
                            ],
                            "MaxHeight": 12,
                            "MinTop": 152,
                        },
                        {
                            "LineText": "가맹점명, 가맹점주소가 실제와 다른경우",
                            "Words": [
                                {
                                    "WordText": "가맹점명",
                                    "Left": 260,
                                    "Top": 128,
                                    "Height": 14,
                                    "Width": 44,
                                },
                                {
                                    "WordText": ",",
                                    "Left": 304,
                                    "Top": 129,
                                    "Height": 13,
                                    "Width": 4,
                                },
                                {
                                    "WordText": "가맹점주소가",
                                    "Left": 309,
                                    "Top": 129,
                                    "Height": 15,
                                    "Width": 69,
                                },
                                {
                                    "WordText": "실제와",
                                    "Left": 378,
                                    "Top": 131,
                                    "Height": 14,
                                    "Width": 36,
                                },
                                {
                                    "WordText": "다른경우",
                                    "Left": 416,
                                    "Top": 132,
                                    "Height": 14,
                                    "Width": 47,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 128,
                        },
                        {
                            "LineText": "신고안내 [포상금 10만원 지금",
                            "Words": [
                                {
                                    "WordText": "신고안내",
                                    "Left": 262,
                                    "Top": 142,
                                    "Height": 14,
                                    "Width": 42,
                                },
                                {
                                    "WordText": "[",
                                    "Left": 306,
                                    "Top": 142,
                                    "Height": 14,
                                    "Width": 7,
                                },
                                {
                                    "WordText": "포상금",
                                    "Left": 313,
                                    "Top": 142,
                                    "Height": 14,
                                    "Width": 31,
                                },
                                {
                                    "WordText": "10",
                                    "Left": 346,
                                    "Top": 142,
                                    "Height": 14,
                                    "Width": 16,
                                },
                                {
                                    "WordText": "만원",
                                    "Left": 362,
                                    "Top": 142,
                                    "Height": 14,
                                    "Width": 21,
                                },
                                {
                                    "WordText": "지금",
                                    "Left": 384,
                                    "Top": 142,
                                    "Height": 14,
                                    "Width": 30,
                                },
                            ],
                            "MaxHeight": 14,
                            "MinTop": 142,
                        },
                        {
                            "LineText": "여신금융협회 : 02-2011-0777",
                            "Words": [
                                {
                                    "WordText": "여신금융협회",
                                    "Left": 260,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 66,
                                },
                                {
                                    "WordText": ":",
                                    "Left": 328,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 5,
                                },
                                {
                                    "WordText": "02",
                                    "Left": 335,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 14,
                                },
                                {
                                    "WordText": "-",
                                    "Left": 349,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 7,
                                },
                                {
                                    "WordText": "2011",
                                    "Left": 356,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 26,
                                },
                                {
                                    "WordText": "-",
                                    "Left": 382,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 5,
                                },
                                {
                                    "WordText": "0777",
                                    "Left": 388,
                                    "Top": 154,
                                    "Height": 14,
                                    "Width": 28,
                                },
                            ],
                            "MaxHeight": 14,
                            "MinTop": 154,
                        },
                        {
                            "LineText": "가맹점",
                            "Words": [
                                {
                                    "WordText": "가맹점",
                                    "Left": 124,
                                    "Top": 214,
                                    "Height": 16,
                                    "Width": 64,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 214,
                        },
                        {
                            "LineText": ": 이화약국",
                            "Words": [
                                {
                                    "WordText": ":",
                                    "Left": 218,
                                    "Top": 214,
                                    "Height": 16,
                                    "Width": 14,
                                },
                                {
                                    "WordText": "이화약국",
                                    "Left": 234,
                                    "Top": 214,
                                    "Height": 17,
                                    "Width": 62,
                                },
                            ],
                            "MaxHeight": 17,
                            "MinTop": 214,
                        },
                        {
                            "LineText": "대표자/전 화",
                            "Words": [
                                {
                                    "WordText": "대표자",
                                    "Left": 126,
                                    "Top": 230,
                                    "Height": 18,
                                    "Width": 47,
                                },
                                {
                                    "WordText": "/",
                                    "Left": 173,
                                    "Top": 230,
                                    "Height": 18,
                                    "Width": 7,
                                },
                                {
                                    "WordText": "전",
                                    "Left": 180,
                                    "Top": 230,
                                    "Height": 18,
                                    "Width": 16,
                                },
                                {
                                    "WordText": "화",
                                    "Left": 198,
                                    "Top": 230,
                                    "Height": 18,
                                    "Width": 18,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 230,
                        },
                        {
                            "LineText": "정은진",
                            "Words": [
                                {
                                    "WordText": "정은진",
                                    "Left": 236,
                                    "Top": 230,
                                    "Height": 18,
                                    "Width": 44,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 230,
                        },
                        {
                            "LineText": "273-5220",
                            "Words": [
                                {
                                    "WordText": "273",
                                    "Left": 336,
                                    "Top": 231,
                                    "Height": 17,
                                    "Width": 24,
                                },
                                {
                                    "WordText": "-",
                                    "Left": 360,
                                    "Top": 232,
                                    "Height": 16,
                                    "Width": 6,
                                },
                                {
                                    "WordText": "5220",
                                    "Left": 366,
                                    "Top": 232,
                                    "Height": 17,
                                    "Width": 32,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 231,
                        },
                        {
                            "LineText": "사업자/단 말",
                            "Words": [
                                {
                                    "WordText": "사업자",
                                    "Left": 124,
                                    "Top": 246,
                                    "Height": 18,
                                    "Width": 47,
                                },
                                {
                                    "WordText": "/",
                                    "Left": 171,
                                    "Top": 246,
                                    "Height": 18,
                                    "Width": 9,
                                },
                                {
                                    "WordText": "단",
                                    "Left": 180,
                                    "Top": 246,
                                    "Height": 18,
                                    "Width": 16,
                                },
                                {
                                    "WordText": "말",
                                    "Left": 198,
                                    "Top": 246,
                                    "Height": 18,
                                    "Width": 18,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 246,
                        },
                        {
                            "LineText": "가맹 번호",
                            "Words": [
                                {
                                    "WordText": "가맹",
                                    "Left": 124,
                                    "Top": 264,
                                    "Height": 16,
                                    "Width": 50,
                                },
                                {
                                    "WordText": "번호",
                                    "Left": 176,
                                    "Top": 264,
                                    "Height": 16,
                                    "Width": 40,
                                },
                            ],
                            "MaxHeight": 16,
                            "MinTop": 264,
                        },
                        {
                            "LineText": ": 506-17-32861",
                            "Words": [
                                {
                                    "WordText": ":",
                                    "Left": 228,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 4,
                                },
                                {
                                    "WordText": "506",
                                    "Left": 234,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 24,
                                },
                                {
                                    "WordText": "-",
                                    "Left": 258,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 8,
                                },
                                {
                                    "WordText": "17",
                                    "Left": 266,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 14,
                                },
                                {
                                    "WordText": "-",
                                    "Left": 280,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 8,
                                },
                                {
                                    "WordText": "32861",
                                    "Left": 288,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 38,
                                },
                            ],
                            "MaxHeight": 16,
                            "MinTop": 248,
                        },
                        {
                            "LineText": "6070009",
                            "Words": [
                                {
                                    "WordText": "6070009",
                                    "Left": 336,
                                    "Top": 248,
                                    "Height": 16,
                                    "Width": 54,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 248,
                        },
                        {
                            "LineText": ": 53918660",
                            "Words": [
                                {
                                    "WordText": ":",
                                    "Left": 222,
                                    "Top": 266,
                                    "Height": 14,
                                    "Width": 10,
                                },
                                {
                                    "WordText": "53918660",
                                    "Left": 234,
                                    "Top": 266,
                                    "Height": 14,
                                    "Width": 64,
                                },
                            ],
                            "MaxHeight": 14,
                            "MinTop": 266,
                        },
                        {
                            "LineText": "주소: 경상북도 포함시 남구 포스코대로353번길 8",
                            "Words": [
                                {
                                    "WordText": "주소",
                                    "Left": 124,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 47,
                                },
                                {
                                    "WordText": ":",
                                    "Left": 172,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 10,
                                },
                                {
                                    "WordText": "경상북도",
                                    "Left": 184,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 63,
                                },
                                {
                                    "WordText": "포함시",
                                    "Left": 249,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 48,
                                },
                                {
                                    "WordText": "남구",
                                    "Left": 299,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 35,
                                },
                                {
                                    "WordText": "포스코대로",
                                    "Left": 337,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 73,
                                },
                                {
                                    "WordText": "353",
                                    "Left": 409,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 22,
                                },
                                {
                                    "WordText": "번길",
                                    "Left": 432,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 30,
                                },
                                {
                                    "WordText": "8",
                                    "Left": 464,
                                    "Top": 280,
                                    "Height": 20,
                                    "Width": 16,
                                },
                            ],
                            "MaxHeight": 20,
                            "MinTop": 280,
                        },
                        {
                            "LineText": "대도동)",
                            "Words": [
                                {
                                    "WordText": "대도동",
                                    "Left": 170,
                                    "Top": 298,
                                    "Height": 16,
                                    "Width": 44,
                                },
                                {
                                    "WordText": ")",
                                    "Left": 214,
                                    "Top": 298,
                                    "Height": 16,
                                    "Width": 10,
                                },
                            ],
                            "MaxHeight": 16,
                            "MinTop": 298,
                        },
                        {
                            "LineText": "[신용구마",
                            "Words": [
                                {
                                    "WordText": "[",
                                    "Left": 232,
                                    "Top": 330,
                                    "Height": 20,
                                    "Width": 15,
                                },
                                {
                                    "WordText": "신용구마",
                                    "Left": 247,
                                    "Top": 330,
                                    "Height": 20,
                                    "Width": 105,
                                },
                            ],
                            "MaxHeight": 20,
                            "MinTop": 330,
                        },
                        {
                            "LineText": "카드",
                            "Words": [
                                {
                                    "WordText": "카드",
                                    "Left": 124,
                                    "Top": 344,
                                    "Height": 18,
                                    "Width": 42,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 344,
                        },
                        {
                            "LineText": "카드",
                            "Words": [
                                {
                                    "WordText": "카드",
                                    "Left": 124,
                                    "Top": 360,
                                    "Height": 18,
                                    "Width": 42,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 360,
                        },
                        {
                            "LineText": "신한카드제크",
                            "Words": [
                                {
                                    "WordText": "신한카드제크",
                                    "Left": 236,
                                    "Top": 361,
                                    "Height": 19,
                                    "Width": 86,
                                }
                            ],
                            "MaxHeight": 19,
                            "MinTop": 361,
                        },
                        {
                            "LineText": "가 맹",
                            "Words": [
                                {
                                    "WordText": "가",
                                    "Left": 124,
                                    "Top": 378,
                                    "Height": 18,
                                    "Width": 20,
                                },
                                {
                                    "WordText": "맹",
                                    "Left": 147,
                                    "Top": 378,
                                    "Height": 18,
                                    "Width": 17,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 378,
                        },
                        {
                            "LineText": "거 래",
                            "Words": [
                                {
                                    "WordText": "거",
                                    "Left": 124,
                                    "Top": 394,
                                    "Height": 18,
                                    "Width": 20,
                                },
                                {
                                    "WordText": "래",
                                    "Left": 147,
                                    "Top": 394,
                                    "Height": 18,
                                    "Width": 17,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 394,
                        },
                        {
                            "LineText": "일",
                            "Words": [
                                {
                                    "WordText": "일",
                                    "Left": 170,
                                    "Top": 396,
                                    "Height": 14,
                                    "Width": 24,
                                }
                            ],
                            "MaxHeight": 14,
                            "MinTop": 396,
                        },
                        {
                            "LineText": "53918660",
                            "Words": [
                                {
                                    "WordText": "53918660",
                                    "Left": 234,
                                    "Top": 380,
                                    "Height": 16,
                                    "Width": 62,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 380,
                        },
                        {
                            "LineText": "시",
                            "Words": [
                                {
                                    "WordText": "시",
                                    "Left": 198,
                                    "Top": 394,
                                    "Height": 18,
                                    "Width": 18,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 394,
                        },
                        {
                            "LineText": "2018/02/08",
                            "Words": [
                                {
                                    "WordText": "2018",
                                    "Left": 230,
                                    "Top": 396,
                                    "Height": 16,
                                    "Width": 36,
                                },
                                {
                                    "WordText": "/",
                                    "Left": 266,
                                    "Top": 396,
                                    "Height": 16,
                                    "Width": 6,
                                },
                                {
                                    "WordText": "02",
                                    "Left": 272,
                                    "Top": 396,
                                    "Height": 16,
                                    "Width": 14,
                                },
                                {
                                    "WordText": "/",
                                    "Left": 286,
                                    "Top": 396,
                                    "Height": 16,
                                    "Width": 8,
                                },
                                {
                                    "WordText": "08",
                                    "Left": 294,
                                    "Top": 396,
                                    "Height": 16,
                                    "Width": 16,
                                },
                            ],
                            "MaxHeight": 16,
                            "MinTop": 396,
                        },
                        {
                            "LineText": "삼품명/제약사",
                            "Words": [
                                {
                                    "WordText": "삼품명",
                                    "Left": 156,
                                    "Top": 425,
                                    "Height": 19,
                                    "Width": 45,
                                },
                                {
                                    "WordText": "/",
                                    "Left": 201,
                                    "Top": 426,
                                    "Height": 18,
                                    "Width": 7,
                                },
                                {
                                    "WordText": "제약사",
                                    "Left": 208,
                                    "Top": 426,
                                    "Height": 19,
                                    "Width": 46,
                                },
                            ],
                            "MaxHeight": 19,
                            "MinTop": 425,
                        },
                        {
                            "LineText": "13:41:24",
                            "Words": [
                                {
                                    "WordText": "13",
                                    "Left": 320,
                                    "Top": 398,
                                    "Height": 16,
                                    "Width": 16,
                                },
                                {
                                    "WordText": ":",
                                    "Left": 336,
                                    "Top": 398,
                                    "Height": 16,
                                    "Width": 8,
                                },
                                {
                                    "WordText": "41",
                                    "Left": 344,
                                    "Top": 398,
                                    "Height": 16,
                                    "Width": 14,
                                },
                                {
                                    "WordText": ":",
                                    "Left": 358,
                                    "Top": 398,
                                    "Height": 16,
                                    "Width": 6,
                                },
                                {
                                    "WordText": "24",
                                    "Left": 364,
                                    "Top": 398,
                                    "Height": 16,
                                    "Width": 18,
                                },
                            ],
                            "MaxHeight": 16,
                            "MinTop": 398,
                        },
                        {
                            "LineText": "단가",
                            "Words": [
                                {
                                    "WordText": "단가",
                                    "Left": 334,
                                    "Top": 428,
                                    "Height": 16,
                                    "Width": 34,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 428,
                        },
                        {
                            "LineText": "01 이가탄에프캡슐",
                            "Words": [
                                {
                                    "WordText": "01",
                                    "Left": 124,
                                    "Top": 458,
                                    "Height": 18,
                                    "Width": 20,
                                },
                                {
                                    "WordText": "이가탄에프캡슐",
                                    "Left": 147,
                                    "Top": 458,
                                    "Height": 18,
                                    "Width": 105,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 458,
                        },
                        {
                            "LineText": "명인제약 (좌",
                            "Words": [
                                {
                                    "WordText": "명인제약",
                                    "Left": 146,
                                    "Top": 474,
                                    "Height": 18,
                                    "Width": 58,
                                },
                                {
                                    "WordText": "(",
                                    "Left": 207,
                                    "Top": 474,
                                    "Height": 18,
                                    "Width": 7,
                                },
                                {
                                    "WordText": "좌",
                                    "Left": 214,
                                    "Top": 474,
                                    "Height": 18,
                                    "Width": 14,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 474,
                        },
                        {
                            "LineText": "27,000",
                            "Words": [
                                {
                                    "WordText": "27,000",
                                    "Left": 318,
                                    "Top": 476,
                                    "Height": 18,
                                    "Width": 48,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 476,
                        },
                        {
                            "LineText": "조 제 의약품",
                            "Words": [
                                {
                                    "WordText": "조",
                                    "Left": 124,
                                    "Top": 506,
                                    "Height": 18,
                                    "Width": 18,
                                },
                                {
                                    "WordText": "제",
                                    "Left": 144,
                                    "Top": 506,
                                    "Height": 18,
                                    "Width": 20,
                                },
                                {
                                    "WordText": "의약품",
                                    "Left": 167,
                                    "Top": 506,
                                    "Height": 18,
                                    "Width": 47,
                                },
                            ],
                            "MaxHeight": 19,
                            "MinTop": 506,
                        },
                        {
                            "LineText": "일반 의약품",
                            "Words": [
                                {
                                    "WordText": "일반",
                                    "Left": 124,
                                    "Top": 522,
                                    "Height": 18,
                                    "Width": 40,
                                },
                                {
                                    "WordText": "의약품",
                                    "Left": 167,
                                    "Top": 522,
                                    "Height": 18,
                                    "Width": 47,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 522,
                        },
                        {
                            "LineText": "합",
                            "Words": [
                                {
                                    "WordText": "합",
                                    "Left": 124,
                                    "Top": 540,
                                    "Height": 16,
                                    "Width": 16,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 540,
                        },
                        {
                            "LineText": "계",
                            "Words": [
                                {
                                    "WordText": "계",
                                    "Left": 196,
                                    "Top": 540,
                                    "Height": 18,
                                    "Width": 16,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 540,
                        },
                        {
                            "LineText": "승인번호",
                            "Words": [
                                {
                                    "WordText": "승인번호",
                                    "Left": 124,
                                    "Top": 572,
                                    "Height": 18,
                                    "Width": 90,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 572,
                        },
                        {
                            "LineText": "매",
                            "Words": [
                                {
                                    "WordText": "매",
                                    "Left": 122,
                                    "Top": 588,
                                    "Height": 18,
                                    "Width": 20,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 588,
                        },
                        {
                            "LineText": "입",
                            "Words": [
                                {
                                    "WordText": "입",
                                    "Left": 142,
                                    "Top": 590,
                                    "Height": 14,
                                    "Width": 36,
                                }
                            ],
                            "MaxHeight": 14,
                            "MinTop": 590,
                        },
                        {
                            "LineText": "사",
                            "Words": [
                                {
                                    "WordText": "사",
                                    "Left": 196,
                                    "Top": 590,
                                    "Height": 18,
                                    "Width": 16,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 590,
                        },
                        {
                            "LineText": "알",
                            "Words": [
                                {
                                    "WordText": "알",
                                    "Left": 122,
                                    "Top": 606,
                                    "Height": 18,
                                    "Width": 18,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 606,
                        },
                        {
                            "LineText": "림",
                            "Words": [
                                {
                                    "WordText": "림",
                                    "Left": 194,
                                    "Top": 608,
                                    "Height": 18,
                                    "Width": 16,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 608,
                        },
                        {
                            "LineText": "1644",
                            "Words": [
                                {
                                    "WordText": "1644",
                                    "Left": 234,
                                    "Top": 574,
                                    "Height": 18,
                                    "Width": 60,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 574,
                        },
                        {
                            "LineText": "0156",
                            "Words": [
                                {
                                    "WordText": "0156",
                                    "Left": 292,
                                    "Top": 574,
                                    "Height": 19,
                                    "Width": 74,
                                }
                            ],
                            "MaxHeight": 19,
                            "MinTop": 574,
                        },
                        {
                            "LineText": "신한카드",
                            "Words": [
                                {
                                    "WordText": "신한카드",
                                    "Left": 232,
                                    "Top": 590,
                                    "Height": 19,
                                    "Width": 60,
                                }
                            ],
                            "MaxHeight": 19,
                            "MinTop": 590,
                        },
                        {
                            "LineText": "KICC로제품",
                            "Words": [
                                {
                                    "WordText": "KICC",
                                    "Left": 232,
                                    "Top": 606,
                                    "Height": 20,
                                    "Width": 62,
                                },
                                {
                                    "WordText": "로제품",
                                    "Left": 295,
                                    "Top": 606,
                                    "Height": 20,
                                    "Width": 84,
                                },
                            ],
                            "MaxHeight": 20,
                            "MinTop": 606,
                        },
                        {
                            "LineText": "*※/*",
                            "Words": [
                                {
                                    "WordText": "*※/*",
                                    "Left": 402,
                                    "Top": 348,
                                    "Height": 14,
                                    "Width": 38,
                                }
                            ],
                            "MaxHeight": 14,
                            "MinTop": 348,
                        },
                        {
                            "LineText": "(일시불)",
                            "Words": [
                                {
                                    "WordText": "(",
                                    "Left": 408,
                                    "Top": 380,
                                    "Height": 18,
                                    "Width": 9,
                                },
                                {
                                    "WordText": "일시불",
                                    "Left": 417,
                                    "Top": 380,
                                    "Height": 18,
                                    "Width": 43,
                                },
                                {
                                    "WordText": ")",
                                    "Left": 460,
                                    "Top": 380,
                                    "Height": 18,
                                    "Width": 8,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 380,
                        },
                        {
                            "LineText": "수량",
                            "Words": [
                                {
                                    "WordText": "수량",
                                    "Left": 386,
                                    "Top": 428,
                                    "Height": 18,
                                    "Width": 30,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 428,
                        },
                        {
                            "LineText": "금액",
                            "Words": [
                                {
                                    "WordText": "금액",
                                    "Left": 444,
                                    "Top": 430,
                                    "Height": 16,
                                    "Width": 30,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 430,
                        },
                        {
                            "LineText": "1",
                            "Words": [
                                {
                                    "WordText": "1",
                                    "Left": 392,
                                    "Top": 476,
                                    "Height": 16,
                                    "Width": 10,
                                }
                            ],
                            "MaxHeight": 16,
                            "MinTop": 476,
                        },
                        {
                            "LineText": "27,000",
                            "Words": [
                                {
                                    "WordText": "27,000",
                                    "Left": 428,
                                    "Top": 478,
                                    "Height": 18,
                                    "Width": 48,
                                }
                            ],
                            "MaxHeight": 18,
                            "MinTop": 478,
                        },
                        {
                            "LineText": "0원",
                            "Words": [
                                {
                                    "WordText": "0",
                                    "Left": 428,
                                    "Top": 510,
                                    "Height": 18,
                                    "Width": 20,
                                },
                                {
                                    "WordText": "원",
                                    "Left": 448,
                                    "Top": 510,
                                    "Height": 18,
                                    "Width": 22,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 510,
                        },
                        {
                            "LineText": "21,000원",
                            "Words": [
                                {
                                    "WordText": "21,000",
                                    "Left": 358,
                                    "Top": 528,
                                    "Height": 16,
                                    "Width": 90,
                                },
                                {
                                    "WordText": "원",
                                    "Left": 448,
                                    "Top": 528,
                                    "Height": 16,
                                    "Width": 18,
                                },
                            ],
                            "MaxHeight": 16,
                            "MinTop": 528,
                        },
                        {
                            "LineText": "27.1",
                            "Words": [
                                {
                                    "WordText": "27.1",
                                    "Left": 360,
                                    "Top": 540,
                                    "Height": 20,
                                    "Width": 46,
                                }
                            ],
                            "MaxHeight": 20,
                            "MinTop": 540,
                        },
                        {
                            "LineText": "000원",
                            "Words": [
                                {
                                    "WordText": "000",
                                    "Left": 402,
                                    "Top": 544,
                                    "Height": 14,
                                    "Width": 45,
                                },
                                {
                                    "WordText": "원",
                                    "Left": 447,
                                    "Top": 544,
                                    "Height": 14,
                                    "Width": 21,
                                },
                            ],
                            "MaxHeight": 14,
                            "MinTop": 544,
                        },
                        {
                            "LineText": "[회원용]",
                            "Words": [
                                {
                                    "WordText": "[",
                                    "Left": 354,
                                    "Top": 642,
                                    "Height": 18,
                                    "Width": 11,
                                },
                                {
                                    "WordText": "회원용",
                                    "Left": 365,
                                    "Top": 642,
                                    "Height": 18,
                                    "Width": 88,
                                },
                                {
                                    "WordText": "]",
                                    "Left": 453,
                                    "Top": 642,
                                    "Height": 18,
                                    "Width": 11,
                                },
                            ],
                            "MaxHeight": 18,
                            "MinTop": 642,
                        },
                        {
                            "LineText": "대경일보",
                            "Words": [
                                {
                                    "WordText": "대경일보",
                                    "Left": 32,
                                    "Top": 718,
                                    "Height": 44,
                                    "Width": 184,
                                }
                            ],
                            "MaxHeight": 44,
                            "MinTop": 718,
                        },
                    ],
                    "HasOverlay": True,
                },
                "FileParseExitCode": 1,
                "TextOrientation": "0",
                "ParsedText": "으팝페이\t가맹점명, 가맹점주소가 실제와 다른경우\t신고안내 [포상금 10만원 지금\t\r\nwww.phampay.co.kr\t여신금융협회 : 02-2011-0777\t\r\n가맹점\t: 이화약국\t\r\n대표자/전 화\t정은진\t273-5220\t\r\n사업자/단 말\t: 506-17-32861\t6070009\t\r\n가맹 번호\t: 53918660\t\r\n주소: 경상북도 포함시 남구 포스코대로353번길 8\t\r\n대도동)\t\r\n[신용구마\t\r\n카드\t*※/*\t\r\n카드\t신한카드제크\t\r\n가 맹\t53918660\t(일시불)\t\r\n거 래\t일\t시\t2018/02/08\t13:41:24\t\r\n삼품명/제약사\t단가\t수량\t금액\t\r\n01 이가탄에프캡슐\t\r\n명인제약 (좌\t27,000\t1\t27,000\t\r\n조 제 의약품\t0원\t\r\n일반 의약품\t21,000원\t\r\n합\t계\t27.1\t000원\t\r\n승인번호\t1644\t0156\t\r\n매\t입\t사\t신한카드\t\r\n알\t림\tKICC로제품\t\r\n[회원용]\t\r\n대경일보\t\r\n",
                "ErrorMessage": "",
                "ErrorDetails": "",
            }
        ],
        "OCRExitCode": 1,
        "IsErroredOnProcessing": False,
        "ProcessingTimeInMilliseconds": 1.547,
        "SearchablePDFURL": "Searchable PDF not generated as it was not requested.",
    }

    result = extract_items_from_ocr(json_data)

    assert len(result) > 0
    assert "이가탄에프캡슐" in result[0]["name"]
    assert result[0]["price"] == 27000
    assert result[0]["quantity"] == 1
    assert result[0]["total"] == 27000

@pytest.mark.asyncio
async def test_get_material_another():
    json_data = {'ParsedResults': [{'TextOverlay': {'Lines': [{'LineText': '럭키할인마트', 'Words': [{'WordText': '럭키할인마트', 'Left': 393.0, 'Top': 79.0, 'Height': 80.0, 'Width': 83.0}], 'MaxHeight': 80.0, 'MinTop': 79.0}, {'LineText': '사업자: 105-18-', 'Words': [{'WordText': '사업자', 'Left': 319.0, 'Top': 53.0, 'Height': 38.0, 'Width': 40.0}, {'WordText': ':', 'Left': 346.0, 'Top': 76.0, 'Height': 14.0, 'Width': 13.0}, {'WordText': '105', 'Left': 348.0, 'Top': 78.0, 'Height': 28.0, 'Width': 29.0}, {'WordText': '-', 'Left': 364.0, 'Top': 92.0, 'Height': 17.0, 'Width': 16.0}, {'WordText': '18', 'Left': 368.0, 'Top': 95.0, 'Height': 22.0, 'Width': 21.0}, {'WordText': '-', 'Left': 377.0, 'Top': 103.0, 'Height': 24.0, 'Width': 22.0}], 'MaxHeight': 74.0, 'MinTop': 53.0}, {'LineText': '주소: 서울 마포구 연남동 565-15', 'Words': [{'WordText': '주소', 'Left': 310.0, 'Top': 63.0, 'Height': 32.0, 'Width': 32.0}, {'WordText': ':', 'Left': 328.0, 'Top': 79.0, 'Height': 17.0, 'Width': 16.0}, {'WordText': '서울', 'Left': 332.0, 'Top': 82.0, 'Height': 31.0, 'Width': 32.0}, {'WordText': '마포구', 'Left': 351.0, 'Top': 100.0, 'Height': 40.0, 'Width': 41.0}, {'WordText': '연남동', 'Left': 381.0, 'Top': 126.0, 'Height': 37.0, 'Width': 37.0}, {'WordText': '565', 'Left': 406.0, 'Top': 149.0, 'Height': 30.0, 'Width': 30.0}, {'WordText': '-', 'Left': 422.0, 'Top': 163.0, 'Height': 19.0, 'Width': 18.0}, {'WordText': '15', 'Left': 425.0, 'Top': 166.0, 'Height': 28.0, 'Width': 28.0}], 'MaxHeight': 132.0, 'MinTop': 63.0}, {'LineText': '대표자: 이재', 'Words': [{'WordText': '대표자', 'Left': 437.0, 'Top': 159.0, 'Height': 45.0, 'Width': 47.0}, {'WordText': ':', 'Left': 470.0, 'Top': 189.0, 'Height': 17.0, 'Width': 15.0}, {'WordText': '이재', 'Left': 474.0, 'Top': 193.0, 'Height': 33.0, 'Width': 33.0}], 'MaxHeight': 66.0, 'MinTop': 159.0}, {'LineText': '전화:02)336-0078', 'Words': [{'WordText': '전화', 'Left': 302.0, 'Top': 74.0, 'Height': 30.0, 'Width': 31.0}, {'WordText': ':', 'Left': 321.0, 'Top': 89.0, 'Height': 18.0, 'Width': 16.0}, {'WordText': '02', 'Left': 324.0, 'Top': 92.0, 'Height': 22.0, 'Width': 21.0}, {'WordText': ')', 'Left': 333.0, 'Top': 100.0, 'Height': 18.0, 'Width': 16.0}, {'WordText': '336', 'Left': 337.0, 'Top': 103.0, 'Height': 27.0, 'Width': 27.0}, {'WordText': '-', 'Left': 351.0, 'Top': 115.0, 'Height': 18.0, 'Width': 16.0}, {'WordText': '0078', 'Left': 355.0, 'Top': 119.0, 'Height': 33.0, 'Width': 34.0}], 'MaxHeight': 77.0, 'MinTop': 74.0}, {'LineText': '2018-01-07일: 001:0194', 'Words': [{'WordText': '2018', 'Left': 295.0, 'Top': 85.0, 'Height': 29.0, 'Width': 29.0}, {'WordText': '-', 'Left': 313.0, 'Top': 101.0, 'Height': 16.0, 'Width': 15.0}, {'WordText': '01', 'Left': 318.0, 'Top': 105.0, 'Height': 19.0, 'Width': 18.0}, {'WordText': '-', 'Left': 325.0, 'Top': 112.0, 'Height': 16.0, 'Width': 15.0}, {'WordText': '07', 'Left': 330.0, 'Top': 116.0, 'Height': 24.0, 'Width': 24.0}, {'WordText': '일', 'Left': 343.0, 'Top': 128.0, 'Height': 19.0, 'Width': 18.0}, {'WordText': ':', 'Left': 350.0, 'Top': 135.0, 'Height': 13.0, 'Width': 12.0}, {'WordText': '001', 'Left': 353.0, 'Top': 138.0, 'Height': 24.0, 'Width': 24.0}, {'WordText': ':', 'Left': 367.0, 'Top': 150.0, 'Height': 16.0, 'Width': 15.0}, {'WordText': '0194', 'Left': 370.0, 'Top': 154.0, 'Height': 29.0, 'Width': 29.0}], 'MaxHeight': 98.0, 'MinTop': 85.0}, {'LineText': '기본사원', 'Words': [{'WordText': '기본사원', 'Left': 430.0, 'Top': 206.0, 'Height': 48.0, 'Width': 50.0}], 'MaxHeight': 48.0, 'MinTop': 206.0}, {'LineText': '상품명', 'Words': [{'WordText': '상품명', 'Left': 276.0, 'Top': 106.0, 'Height': 42.0, 'Width': 42.0}], 'MaxHeight': 42.0, 'MinTop': 106.0}, {'LineText': '해표 더고소한길16봉', 'Words': [{'WordText': '해표', 'Left': 258.0, 'Top': 126.0, 'Height': 28.0, 'Width': 27.0}, {'WordText': '더고소한길', 'Left': 275.0, 'Top': 140.0, 'Height': 52.0, 'Width': 55.0}, {'WordText': '16', 'Left': 318.0, 'Top': 178.0, 'Height': 22.0, 'Width': 21.0}, {'WordText': '봉', 'Left': 326.0, 'Top': 186.0, 'Height': 26.0, 'Width': 26.0}], 'MaxHeight': 86.0, 'MinTop': 126.0}, {'LineText': '*깊은산속맑은알30구', 'Words': [{'WordText': '*', 'Left': 250.0, 'Top': 136.0, 'Height': 20.0, 'Width': 19.0}, {'WordText': '깊은산속맑은알', 'Left': 258.0, 'Top': 143.0, 'Height': 61.0, 'Width': 68.0}, {'WordText': '30', 'Left': 315.0, 'Top': 191.0, 'Height': 21.0, 'Width': 21.0}, {'WordText': '구', 'Left': 325.0, 'Top': 199.0, 'Height': 21.0, 'Width': 20.0}], 'MaxHeight': 84.0, 'MinTop': 136.0}, {'LineText': '곤약250g', 'Words': [{'WordText': '곤약', 'Left': 266.0, 'Top': 164.0, 'Height': 27.0, 'Width': 28.0}, {'WordText': '250g', 'Left': 282.0, 'Top': 179.0, 'Height': 31.0, 'Width': 32.0}], 'MaxHeight': 46.0, 'MinTop': 164.0}, {'LineText': '단가 수량', 'Words': [{'WordText': '단가', 'Left': 378.0, 'Top': 196.0, 'Height': 30.0, 'Width': 31.0}, {'WordText': '수량', 'Left': 398.0, 'Top': 213.0, 'Height': 33.0, 'Width': 34.0}], 'MaxHeight': 50.0, 'MinTop': 196.0}, {'LineText': '3,300', 'Words': [{'WordText': '3,300', 'Left': 356.0, 'Top': 211.0, 'Height': 36.0, 'Width': 40.0}], 'MaxHeight': 36.0, 'MinTop': 211.0}, {'LineText': '1,000', 'Words': [{'WordText': '1,000', 'Left': 343.0, 'Top': 231.0, 'Height': 32.0, 'Width': 34.0}], 'MaxHeight': 32.0, 'MinTop': 231.0}, {'LineText': '1,300', 'Words': [{'WordText': '1,300', 'Left': 333.0, 'Top': 237.0, 'Height': 37.0, 'Width': 37.0}], 'MaxHeight': 37.0, 'MinTop': 237.0}, {'LineText': '부가세 면세상품입니다', 'Words': [{'WordText': '부가세', 'Left': 305.0, 'Top': 243.0, 'Height': 37.0, 'Width': 38.0}, {'WordText': '면세상품입니다', 'Left': 331.0, 'Top': 266.0, 'Height': 66.0, 'Width': 71.0}], 'MaxHeight': 90.0, 'MinTop': 243.0}, {'LineText': '과세용금액:', 'Words': [{'WordText': '과세용금액', 'Left': 269.0, 'Top': 238.0, 'Height': 62.0, 'Width': 66.0}, {'WordText': ':', 'Left': 319.0, 'Top': 284.0, 'Height': 16.0, 'Width': 16.0}], 'MaxHeight': 62.0, 'MinTop': 238.0}, {'LineText': '3,900', 'Words': [{'WordText': '3,900', 'Left': 348.0, 'Top': 311.0, 'Height': 35.0, 'Width': 39.0}], 'MaxHeight': 35.0, 'MinTop': 311.0}, {'LineText': '면세용품:', 'Words': [{'WordText': '면세용품', 'Left': 252.0, 'Top': 254.0, 'Height': 53.0, 'Width': 53.0}, {'WordText': ':', 'Left': 286.0, 'Top': 288.0, 'Height': 18.0, 'Width': 19.0}], 'MaxHeight': 53.0, 'MinTop': 254.0}, {'LineText': '5,800', 'Words': [{'WordText': '5,800', 'Left': 333.0, 'Top': 329.0, 'Height': 35.0, 'Width': 37.0}], 'MaxHeight': 35.0, 'MinTop': 329.0}, {'LineText': '3,300', 'Words': [{'WordText': '3,300', 'Left': 406.0, 'Top': 255.0, 'Height': 36.0, 'Width': 40.0}], 'MaxHeight': 36.0, 'MinTop': 255.0}, {'LineText': '신용카드:', 'Words': [{'WordText': '신용카드', 'Left': 208.0, 'Top': 280.0, 'Height': 56.0, 'Width': 56.0}, {'WordText': ':', 'Left': 241.0, 'Top': 312.0, 'Height': 33.0, 'Width': 32.0}], 'MaxHeight': 65.0, 'MinTop': 280.0}, {'LineText': '[승인번사] KIS', 'Words': [{'WordText': '[', 'Left': 129.0, 'Top': 268.0, 'Height': 23.0, 'Width': 22.0}, {'WordText': '승인번사', 'Left': 138.0, 'Top': 275.0, 'Height': 41.0, 'Width': 44.0}, {'WordText': ']', 'Left': 168.0, 'Top': 300.0, 'Height': 19.0, 'Width': 17.0}, {'WordText': 'KIS', 'Left': 174.0, 'Top': 305.0, 'Height': 34.0, 'Width': 34.0}], 'MaxHeight': 71.0, 'MinTop': 268.0}, {'LineText': '[ 승인일시] 1R0107', 'Words': [{'WordText': '[', 'Left': 113.0, 'Top': 290.0, 'Height': 24.0, 'Width': 24.0}, {'WordText': '승인일시', 'Left': 127.0, 'Top': 301.0, 'Height': 41.0, 'Width': 45.0}, {'WordText': ']', 'Left': 160.0, 'Top': 328.0, 'Height': 18.0, 'Width': 17.0}, {'WordText': '1R0107', 'Left': 167.0, 'Top': 334.0, 'Height': 33.0, 'Width': 34.0}], 'MaxHeight': 76.0, 'MinTop': 290.0}, {'LineText': '1B제크카드', 'Words': [{'WordText': '1B', 'Left': 122.0, 'Top': 349.0, 'Height': 34.0, 'Width': 32.0}, {'WordText': '제크카드', 'Left': 132.0, 'Top': 358.0, 'Height': 62.0, 'Width': 63.0}], 'MaxHeight': 70.0, 'MinTop': 349.0}, {'LineText': 'KB카', 'Words': [{'WordText': 'KB', 'Left': 109.0, 'Top': 366.0, 'Height': 42.0, 'Width': 45.0}, {'WordText': '카', 'Left': 140.0, 'Top': 384.0, 'Height': 29.0, 'Width': 23.0}], 'MaxHeight': 47.0, 'MinTop': 366.0}, {'LineText': '매출일시: 2018', 'Words': [{'WordText': '매출일시', 'Left': 27.0, 'Top': 427.0, 'Height': 45.0, 'Width': 50.0}, {'WordText': ':', 'Left': 65.0, 'Top': 456.0, 'Height': 17.0, 'Width': 13.0}, {'WordText': '2018', 'Left': 68.0, 'Top': 459.0, 'Height': 31.0, 'Width': 32.0}], 'MaxHeight': 63.0, 'MinTop': 427.0}], 'HasOverlay': True}, 'TextOrientation': '0', 'FileParseExitCode': 1, 'ParsedText': '상품명\t2018-01-07일: 001:0194\t전화:02)336-0078\t주소: 서울 마포구 연남동 565-15\t사업자: 105-18-\t럭키할인마트\t\r\n*깊은산속맑은알30구\t해표 더고소한길16봉\t곤약250g\t단가 수량\t대표자: 이재\t\r\n1,000\t3,300\t기본사원\t\r\n과세용금액:\t1,300\t3,300\t\r\n[ 승인일시] 1R0107\t[승인번사] KIS\t신용카드:\t면세용품:\t부가세 면세상품입니다\t3,900\t\r\n5,800\t\r\nKB카\t1B제크카드\t\r\n매출일시: 2018\t\r\n', 'ErrorMessage': '', 'ErrorDetails': ''}], 'OCRExitCode': 1, 'IsErroredOnProcessing': False, 'ProcessingTimeInMilliseconds': '1266', 'SearchablePDFURL': 'Searchable PDF not generated as it was not requested.'}

    result = extract_items_from_ocr(json_data, 300, 30)

    assert len(result) > 0
    assert "해표" in result[0]["name"]
