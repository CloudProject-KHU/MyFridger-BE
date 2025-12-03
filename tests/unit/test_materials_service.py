import pytest
from app.services.materials import extract_items_from_ocr

test_data_1 = {
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
test_data_2 = {'ParsedResults': [{'TextOverlay': {'Lines': [{'LineText': '영수증 미지참시 교환/환불 불가', 'Words': [{'WordText': '영수증', 'Left': 76.0, 'Top': 0.0, 'Height': 22.0, 'Width': 66.0}, {'WordText': '미지참시', 'Left': 145.0, 'Top': 0.0, 'Height': 22.0, 'Width': 91.0}, {'WordText': '교환', 'Left': 238.0, 'Top': 0.0, 'Height': 22.0, 'Width': 44.0}, {'WordText': '/', 'Left': 282.0, 'Top': 0.0, 'Height': 22.0, 'Width': 11.0}, {'WordText': '환불', 'Left': 293.0, 'Top': 0.0, 'Height': 22.0, 'Width': 44.0}, {'WordText': '불가', 'Left': 340.0, 'Top': 0.0, 'Height': 22.0, 'Width': 46.0}], 'MaxHeight': 22.0, 'MinTop': 0.0}, {'LineText': '※ 정상상품에 한함, 30일 이내(신설 7일)', 'Words': [{'WordText': '※', 'Left': 72.0, 'Top': 14.0, 'Height': 26.0, 'Width': 26.0}, {'WordText': '정상상품에', 'Left': 101.0, 'Top': 14.0, 'Height': 26.0, 'Width': 107.0}, {'WordText': '한함', 'Left': 212.0, 'Top': 14.0, 'Height': 26.0, 'Width': 45.0}, {'WordText': ',', 'Left': 257.0, 'Top': 14.0, 'Height': 26.0, 'Width': 13.0}, {'WordText': '30', 'Left': 273.0, 'Top': 14.0, 'Height': 26.0, 'Width': 29.0}, {'WordText': '일', 'Left': 303.0, 'Top': 14.0, 'Height': 26.0, 'Width': 23.0}, {'WordText': '이내', 'Left': 329.0, 'Top': 14.0, 'Height': 26.0, 'Width': 45.0}, {'WordText': '(', 'Left': 374.0, 'Top': 14.0, 'Height': 26.0, 'Width': 13.0}, {'WordText': '신설', 'Left': 387.0, 'Top': 14.0, 'Height': 26.0, 'Width': 42.0}, {'WordText': '7', 'Left': 433.0, 'Top': 14.0, 'Height': 26.0, 'Width': 16.0}, {'WordText': '일', 'Left': 449.0, 'Top': 14.0, 'Height': 26.0, 'Width': 19.0}, {'WordText': ')', 'Left': 468.0, 'Top': 14.0, 'Height': 26.0, 'Width': 14.0}], 'MaxHeight': 26.0, 'MinTop': 14.0}, {'LineText': '교환/환불 구매점에서 가능(결제카드지참)', 'Words': [{'WordText': '교환', 'Left': 64.0, 'Top': 34.0, 'Height': 24.0, 'Width': 45.0}, {'WordText': '/', 'Left': 109.0, 'Top': 34.0, 'Height': 24.0, 'Width': 12.0}, {'WordText': '환불', 'Left': 121.0, 'Top': 34.0, 'Height': 24.0, 'Width': 48.0}, {'WordText': '구매점에서', 'Left': 172.0, 'Top': 34.0, 'Height': 24.0, 'Width': 111.0}, {'WordText': '가능', 'Left': 286.0, 'Top': 34.0, 'Height': 24.0, 'Width': 45.0}, {'WordText': '(', 'Left': 331.0, 'Top': 34.0, 'Height': 24.0, 'Width': 12.0}, {'WordText': '결제카드지참', 'Left': 343.0, 'Top': 34.0, 'Height': 24.0, 'Width': 129.0}, {'WordText': ')', 'Left': 472.0, 'Top': 34.0, 'Height': 24.0, 'Width': 12.0}], 'MaxHeight': 24.0, 'MinTop': 34.0}, {'LineText': '[구 매]2017-06-02 21:13', 'Words': [{'WordText': '[', 'Left': 56.0, 'Top': 76.0, 'Height': 22.0, 'Width': 14.0}, {'WordText': '구', 'Left': 70.0, 'Top': 76.0, 'Height': 22.0, 'Width': 25.0}, {'WordText': '매', 'Left': 97.0, 'Top': 76.0, 'Height': 22.0, 'Width': 25.0}, {'WordText': ']', 'Left': 122.0, 'Top': 76.0, 'Height': 22.0, 'Width': 11.0}, {'WordText': '2017', 'Left': 133.0, 'Top': 76.0, 'Height': 22.0, 'Width': 44.0}, {'WordText': '-', 'Left': 177.0, 'Top': 76.0, 'Height': 22.0, 'Width': 11.0}, {'WordText': '06', 'Left': 188.0, 'Top': 76.0, 'Height': 22.0, 'Width': 22.0}, {'WordText': '-', 'Left': 210.0, 'Top': 76.0, 'Height': 22.0, 'Width': 11.0}, {'WordText': '02', 'Left': 221.0, 'Top': 76.0, 'Height': 22.0, 'Width': 28.0}, {'WordText': '21', 'Left': 251.0, 'Top': 76.0, 'Height': 22.0, 'Width': 25.0}, {'WordText': ':', 'Left': 276.0, 'Top': 76.0, 'Height': 22.0, 'Width': 11.0}, {'WordText': '13', 'Left': 287.0, 'Top': 76.0, 'Height': 22.0, 'Width': 25.0}], 'MaxHeight': 22.0, 'MinTop': 76.0}, {'LineText': '상품 명', 'Words': [{'WordText': '상품', 'Left': 80.0, 'Top': 120.0, 'Height': 22.0, 'Width': 66.0}, {'WordText': '명', 'Left': 149.0, 'Top': 120.0, 'Height': 22.0, 'Width': 23.0}], 'MaxHeight': 22.0, 'MinTop': 120.0}, {'LineText': '단•가', 'Words': [{'WordText': '단', 'Left': 308.0, 'Top': 120.0, 'Height': 22.0, 'Width': 33.0}, {'WordText': '•', 'Left': 341.0, 'Top': 120.0, 'Height': 22.0, 'Width': 14.0}, {'WordText': '가', 'Left': 355.0, 'Top': 120.0, 'Height': 22.0, 'Width': 21.0}], 'MaxHeight': 22.0, 'MinTop': 120.0}, {'LineText': '수량', 'Words': [{'WordText': '수량', 'Left': 396.0, 'Top': 120.0, 'Height': 22.0, 'Width': 52.0}], 'MaxHeight': 22.0, 'MinTop': 120.0}, {'LineText': 'POS: 1021-5338', 'Words': [{'WordText': 'POS', 'Left': 418.0, 'Top': 72.0, 'Height': 22.0, 'Width': 39.0}, {'WordText': ':', 'Left': 457.0, 'Top': 72.0, 'Height': 22.0, 'Width': 3.0}, {'WordText': '1021', 'Left': 462.0, 'Top': 72.0, 'Height': 22.0, 'Width': 50.0}, {'WordText': '-', 'Left': 512.0, 'Top': 72.0, 'Height': 22.0, 'Width': 8.0}, {'WordText': '5338', 'Left': 520.0, 'Top': 72.0, 'Height': 22.0, 'Width': 48.0}], 'MaxHeight': 22.0, 'MinTop': 72.0}, {'LineText': '금', 'Words': [{'WordText': '금', 'Left': 494.0, 'Top': 118.0, 'Height': 26.0, 'Width': 24.0}], 'MaxHeight': 26.0, 'MinTop': 118.0}, {'LineText': '액', 'Words': [{'WordText': '액', 'Left': 528.0, 'Top': 116.0, 'Height': 24.0, 'Width': 38.0}], 'MaxHeight': 24.0, 'MinTop': 116.0}, {'LineText': '01* 노브랜드 굿밀크우', 'Words': [{'WordText': '01', 'Left': 40.0, 'Top': 172.0, 'Height': 30.0, 'Width': 22.0}, {'WordText': '*', 'Left': 62.0, 'Top': 172.0, 'Height': 30.0, 'Width': 30.0}, {'WordText': '노브랜드', 'Left': 96.0, 'Top': 172.0, 'Height': 30.0, 'Width': 101.0}, {'WordText': '굿밀크우', 'Left': 201.0, 'Top': 172.0, 'Height': 30.0, 'Width': 97.0}], 'MaxHeight': 30.0, 'MinTop': 172.0}, {'LineText': '1,680', 'Words': [{'WordText': '1,680', 'Left': 352.0, 'Top': 174.0, 'Height': 32.0, 'Width': 62.0}], 'MaxHeight': 32.0, 'MinTop': 174.0}, {'LineText': '02', 'Words': [{'WordText': '02', 'Left': 40.0, 'Top': 204.0, 'Height': 24.0, 'Width': 30.0}], 'MaxHeight': 24.0, 'MinTop': 204.0}, {'LineText': '03', 'Words': [{'WordText': '03', 'Left': 40.0, 'Top': 234.0, 'Height': 26.0, 'Width': 30.0}], 'MaxHeight': 26.0, 'MinTop': 234.0}, {'LineText': '스마트알뜰양복커버', 'Words': [{'WordText': '스마트알뜰양복커버', 'Left': 100.0, 'Top': 204.0, 'Height': 30.0, 'Width': 208.0}], 'MaxHeight': 30.0, 'MinTop': 204.0}, {'LineText': '2,590', 'Words': [{'WordText': '2,590', 'Left': 350.0, 'Top': 206.0, 'Height': 30.0, 'Width': 64.0}], 'MaxHeight': 30.0, 'MinTop': 206.0}, {'LineText': '농심 포스틱 84g', 'Words': [{'WordText': '농심', 'Left': 100.0, 'Top': 234.0, 'Height': 30.0, 'Width': 49.0}, {'WordText': '포스틱', 'Left': 152.0, 'Top': 234.0, 'Height': 30.0, 'Width': 75.0}, {'WordText': '84g', 'Left': 231.0, 'Top': 234.0, 'Height': 30.0, 'Width': 45.0}], 'MaxHeight': 31.0, 'MinTop': 234.0}, {'LineText': '1,120', 'Words': [{'WordText': '1,120', 'Left': 350.0, 'Top': 236.0, 'Height': 32.0, 'Width': 62.0}], 'MaxHeight': 32.0, 'MinTop': 236.0}, {'LineText': '04', 'Words': [{'WordText': '04', 'Left': 42.0, 'Top': 266.0, 'Height': 24.0, 'Width': 28.0}], 'MaxHeight': 24.0, 'MinTop': 266.0}, {'LineText': '농심 올리브짜파게', 'Words': [{'WordText': '농심', 'Left': 102.0, 'Top': 266.0, 'Height': 28.0, 'Width': 49.0}, {'WordText': '올리브짜파게', 'Left': 154.0, 'Top': 266.0, 'Height': 28.0, 'Width': 142.0}], 'MaxHeight': 28.0, 'MinTop': 266.0}, {'LineText': '3,850', 'Words': [{'WordText': '3,850', 'Left': 348.0, 'Top': 267.0, 'Height': 31.0, 'Width': 65.0}], 'MaxHeight': 31.0, 'MinTop': 267.0}, {'LineText': '05*', 'Words': [{'WordText': '05', 'Left': 42.0, 'Top': 296.0, 'Height': 26.0, 'Width': 23.0}, {'WordText': '*', 'Left': 65.0, 'Top': 296.0, 'Height': 26.0, 'Width': 17.0}], 'MaxHeight': 26.0, 'MinTop': 296.0}, {'LineText': '산딸기 500g/박스', 'Words': [{'WordText': '산딸기', 'Left': 102.0, 'Top': 296.0, 'Height': 28.0, 'Width': 70.0}, {'WordText': '500g', 'Left': 175.0, 'Top': 296.0, 'Height': 28.0, 'Width': 52.0}, {'WordText': '/', 'Left': 228.0, 'Top': 296.0, 'Height': 28.0, 'Width': 10.0}, {'WordText': '박스', 'Left': 238.0, 'Top': 296.0, 'Height': 28.0, 'Width': 48.0}], 'MaxHeight': 28.0, 'MinTop': 296.0}, {'LineText': '6,980', 'Words': [{'WordText': '6,980', 'Left': 348.0, 'Top': 298.0, 'Height': 31.0, 'Width': 62.0}], 'MaxHeight': 31.0, 'MinTop': 298.0}, {'LineText': '06', 'Words': [{'WordText': '06', 'Left': 42.0, 'Top': 326.0, 'Height': 26.0, 'Width': 30.0}], 'MaxHeight': 26.0, 'MinTop': 326.0}, {'LineText': '(G)서핑여워터슈NY', 'Words': [{'WordText': '(', 'Left': 102.0, 'Top': 326.0, 'Height': 28.0, 'Width': 10.0}, {'WordText': 'G', 'Left': 112.0, 'Top': 326.0, 'Height': 28.0, 'Width': 14.0}, {'WordText': ')', 'Left': 126.0, 'Top': 326.0, 'Height': 28.0, 'Width': 14.0}, {'WordText': '서핑여워터슈', 'Left': 141.0, 'Top': 326.0, 'Height': 28.0, 'Width': 129.0}, {'WordText': 'NY', 'Left': 270.0, 'Top': 326.0, 'Height': 28.0, 'Width': 26.0}], 'MaxHeight': 28.0, 'MinTop': 326.0}, {'LineText': '19,800', 'Words': [{'WordText': '19,800', 'Left': 338.0, 'Top': 328.0, 'Height': 29.0, 'Width': 72.0}], 'MaxHeight': 29.0, 'MinTop': 328.0}, {'LineText': '07', 'Words': [{'WordText': '07', 'Left': 44.0, 'Top': 358.0, 'Height': 24.0, 'Width': 28.0}], 'MaxHeight': 24.0, 'MinTop': 358.0}, {'LineText': '대여용부직포쇼핑백', 'Words': [{'WordText': '대여용부직포쇼핑백', 'Left': 94.0, 'Top': 356.0, 'Height': 32.0, 'Width': 212.0}], 'MaxHeight': 32.0, 'MinTop': 356.0}, {'LineText': '500', 'Words': [{'WordText': '500', 'Left': 370.0, 'Top': 358.0, 'Height': 24.0, 'Width': 38.0}], 'MaxHeight': 24.0, 'MinTop': 358.0}, {'LineText': '08*', 'Words': [{'WordText': '08', 'Left': 44.0, 'Top': 386.0, 'Height': 26.0, 'Width': 23.0}, {'WordText': '*', 'Left': 67.0, 'Top': 386.0, 'Height': 26.0, 'Width': 17.0}], 'MaxHeight': 26.0, 'MinTop': 386.0}, {'LineText': '호주곡물오이스터블', 'Words': [{'WordText': '호주곡물오이스터블', 'Left': 104.0, 'Top': 386.0, 'Height': 28.0, 'Width': 202.0}], 'MaxHeight': 28.0, 'MinTop': 386.0}, {'LineText': '14,720', 'Words': [{'WordText': '14,720', 'Left': 334.0, 'Top': 388.0, 'Height': 30.0, 'Width': 74.0}], 'MaxHeight': 30.0, 'MinTop': 388.0}, {'LineText': '09', 'Words': [{'WordText': '09', 'Left': 44.0, 'Top': 416.0, 'Height': 26.0, 'Width': 28.0}], 'MaxHeight': 26.0, 'MinTop': 416.0}, {'LineText': '오뚜기 콤비네이션', 'Words': [{'WordText': '오뚜기', 'Left': 104.0, 'Top': 414.0, 'Height': 28.0, 'Width': 73.0}, {'WordText': '콤비네이션', 'Left': 181.0, 'Top': 414.0, 'Height': 28.0, 'Width': 117.0}], 'MaxHeight': 28.0, 'MinTop': 414.0}, {'LineText': '5,980', 'Words': [{'WordText': '5,980', 'Left': 344.0, 'Top': 416.0, 'Height': 30.0, 'Width': 62.0}], 'MaxHeight': 30.0, 'MinTop': 416.0}, {'LineText': '10', 'Words': [{'WordText': '10', 'Left': 46.0, 'Top': 446.0, 'Height': 24.0, 'Width': 28.0}], 'MaxHeight': 24.0, 'MinTop': 446.0}, {'LineText': '• 꼬깔콘허니버터 132G', 'Words': [{'WordText': '•', 'Left': 82.0, 'Top': 444.0, 'Height': 28.0, 'Width': 14.0}, {'WordText': '꼬깔콘허니버터', 'Left': 100.0, 'Top': 444.0, 'Height': 28.0, 'Width': 154.0}, {'WordText': '132G', 'Left': 257.0, 'Top': 444.0, 'Height': 28.0, 'Width': 51.0}], 'MaxHeight': 28.0, 'MinTop': 444.0}, {'LineText': '1,580', 'Words': [{'WordText': '1,580', 'Left': 346.0, 'Top': 446.0, 'Height': 28.0, 'Width': 76.0}], 'MaxHeight': 28.0, 'MinTop': 446.0}, {'LineText': 'CJ미니드레싱골라담', 'Words': [{'WordText': 'CJ', 'Left': 102.0, 'Top': 472.0, 'Height': 28.0, 'Width': 24.0}, {'WordText': '미니드레싱골라담', 'Left': 127.0, 'Top': 472.0, 'Height': 28.0, 'Width': 180.0}], 'MaxHeight': 28.0, 'MinTop': 472.0}, {'LineText': '5, 900', 'Words': [{'WordText': '5', 'Left': 348.0, 'Top': 479.0, 'Height': 16.0, 'Width': 10.0}, {'WordText': ',', 'Left': 358.0, 'Top': 480.0, 'Height': 16.0, 'Width': 6.0}, {'WordText': '900', 'Left': 366.0, 'Top': 480.0, 'Height': 17.0, 'Width': 32.0}], 'MaxHeight': 17.0, 'MinTop': 479.0}, {'LineText': '12', 'Words': [{'WordText': '12', 'Left': 46.0, 'Top': 506.0, 'Height': 24.0, 'Width': 26.0}], 'MaxHeight': 24.0, 'MinTop': 506.0}, {'LineText': '청정원허브맛솔트(', 'Words': [{'WordText': '청정원허브맛솔트', 'Left': 104.0, 'Top': 500.0, 'Height': 32.0, 'Width': 176.0}, {'WordText': '(', 'Left': 280.0, 'Top': 500.0, 'Height': 32.0, 'Width': 16.0}], 'MaxHeight': 32.0, 'MinTop': 500.0}, {'LineText': '1,980', 'Words': [{'WordText': '1,980', 'Left': 344.0, 'Top': 500.0, 'Height': 28.0, 'Width': 60.0}], 'MaxHeight': 28.0, 'MinTop': 500.0}, {'LineText': '13*', 'Words': [{'WordText': '13', 'Left': 46.0, 'Top': 536.0, 'Height': 22.0, 'Width': 22.0}, {'WordText': '*', 'Left': 68.0, 'Top': 536.0, 'Height': 22.0, 'Width': 16.0}], 'MaxHeight': 22.0, 'MinTop': 536.0}, {'LineText': '태국미니아스파라거', 'Words': [{'WordText': '태국미니아스파라거', 'Left': 103.0, 'Top': 527.0, 'Height': 32.0, 'Width': 201.0}], 'MaxHeight': 32.0, 'MinTop': 527.0}, {'LineText': '4,580', 'Words': [{'WordText': '4,580', 'Left': 342.0, 'Top': 528.0, 'Height': 29.0, 'Width': 60.0}], 'MaxHeight': 29.0, 'MinTop': 528.0}, {'LineText': '14', 'Words': [{'WordText': '14', 'Left': 46.0, 'Top': 564.0, 'Height': 24.0, 'Width': 28.0}], 'MaxHeight': 24.0, 'MinTop': 564.0}, {'LineText': '. 롯데 수박바젤리 56', 'Words': [{'WordText': '.', 'Left': 79.0, 'Top': 561.0, 'Height': 28.0, 'Width': 18.0}, {'WordText': '롯데', 'Left': 100.0, 'Top': 559.0, 'Height': 29.0, 'Width': 55.0}, {'WordText': '수박바젤리', 'Left': 157.0, 'Top': 555.0, 'Height': 31.0, 'Width': 116.0}, {'WordText': '56', 'Left': 275.0, 'Top': 554.0, 'Height': 29.0, 'Width': 32.0}], 'MaxHeight': 35.0, 'MinTop': 554.0}, {'LineText': '980', 'Words': [{'WordText': '980', 'Left': 364.0, 'Top': 556.0, 'Height': 24.0, 'Width': 38.0}], 'MaxHeight': 24.0, 'MinTop': 556.0}, {'LineText': '15', 'Words': [{'WordText': '15', 'Left': 46.0, 'Top': 592.0, 'Height': 24.0, 'Width': 28.0}], 'MaxHeight': 24.0, 'MinTop': 592.0}, {'LineText': '바리스타 쇼콜라 32', 'Words': [{'WordText': '바리스타', 'Left': 102.0, 'Top': 586.0, 'Height': 28.0, 'Width': 94.0}, {'WordText': '쇼콜라', 'Left': 200.0, 'Top': 586.0, 'Height': 28.0, 'Width': 73.0}, {'WordText': '32', 'Left': 277.0, 'Top': 586.0, 'Height': 28.0, 'Width': 29.0}], 'MaxHeight': 28.0, 'MinTop': 586.0}, {'LineText': '2,250', 'Words': [{'WordText': '2,250', 'Left': 342.0, 'Top': 584.0, 'Height': 30.0, 'Width': 60.0}], 'MaxHeight': 30.0, 'MinTop': 584.0}, {'LineText': '(*)면 세', 'Words': [{'WordText': '(*)', 'Left': 180.0, 'Top': 616.0, 'Height': 28.0, 'Width': 38.0}, {'WordText': '면', 'Left': 218.0, 'Top': 616.0, 'Height': 28.0, 'Width': 24.0}, {'WordText': '세', 'Left': 246.0, 'Top': 616.0, 'Height': 28.0, 'Width': 26.0}], 'MaxHeight': 28.0, 'MinTop': 616.0}, {'LineText': '[ 물품', 'Words': [{'WordText': '[', 'Left': 266.0, 'Top': 618.0, 'Height': 22.0, 'Width': 22.0}, {'WordText': '물품', 'Left': 291.0, 'Top': 618.0, 'Height': 22.0, 'Width': 55.0}], 'MaxHeight': 22.0, 'MinTop': 618.0}, {'LineText': '과세 물품', 'Words': [{'WordText': '과세', 'Left': 216.0, 'Top': 644.0, 'Height': 28.0, 'Width': 70.0}, {'WordText': '물품', 'Left': 289.0, 'Top': 644.0, 'Height': 28.0, 'Width': 61.0}], 'MaxHeight': 28.0, 'MinTop': 644.0}, {'LineText': '. 부가 세', 'Words': [{'WordText': '.', 'Left': 194.0, 'Top': 681.0, 'Height': 28.0, 'Width': 15.0}, {'WordText': '부가', 'Left': 211.0, 'Top': 673.0, 'Height': 35.0, 'Width': 106.0}, {'WordText': '세', 'Left': 319.0, 'Top': 670.0, 'Height': 29.0, 'Width': 29.0}], 'MaxHeight': 39.0, 'MinTop': 670.0}, {'LineText': '합', 'Words': [{'WordText': '합', 'Left': 214.0, 'Top': 706.0, 'Height': 28.0, 'Width': 24.0}], 'MaxHeight': 28.0, 'MinTop': 706.0}, {'LineText': '계', 'Words': [{'WordText': '계', 'Left': 312.0, 'Top': 704.0, 'Height': 26.0, 'Width': 36.0}], 'MaxHeight': 26.0, 'MinTop': 704.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 446.0, 'Top': 178.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 178.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 444.0, 'Top': 240.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 240.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 444.0, 'Top': 270.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 270.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 442.0, 'Top': 300.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 300.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 438.0, 'Top': 330.0, 'Height': 22.0, 'Width': 14.0}], 'MaxHeight': 22.0, 'MinTop': 330.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 440.0, 'Top': 360.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 360.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 440.0, 'Top': 390.0, 'Height': 20.0, 'Width': 8.0}], 'MaxHeight': 20.0, 'MinTop': 390.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 436.0, 'Top': 420.0, 'Height': 20.0, 'Width': 12.0}], 'MaxHeight': 20.0, 'MinTop': 420.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 436.0, 'Top': 448.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 448.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 434.0, 'Top': 476.0, 'Height': 18.0, 'Width': 10.0}], 'MaxHeight': 18.0, 'MinTop': 476.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 434.0, 'Top': 504.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 504.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 432.0, 'Top': 532.0, 'Height': 18.0, 'Width': 10.0}], 'MaxHeight': 18.0, 'MinTop': 532.0}, {'LineText': '2', 'Words': [{'WordText': '2', 'Left': 428.0, 'Top': 558.0, 'Height': 22.0, 'Width': 14.0}], 'MaxHeight': 22.0, 'MinTop': 558.0}, {'LineText': '1', 'Words': [{'WordText': '1', 'Left': 430.0, 'Top': 586.0, 'Height': 20.0, 'Width': 10.0}], 'MaxHeight': 20.0, 'MinTop': 586.0}, {'LineText': '결제 대상 금액', 'Words': [{'WordText': '결제', 'Left': 48.0, 'Top': 736.0, 'Height': 28.0, 'Width': 59.0}, {'WordText': '대상', 'Left': 111.0, 'Top': 736.0, 'Height': 28.0, 'Width': 63.0}, {'WordText': '금액', 'Left': 177.0, 'Top': 736.0, 'Height': 28.0, 'Width': 63.0}], 'MaxHeight': 28.0, 'MinTop': 736.0}, {'LineText': '1,680', 'Words': [{'WordText': '1,680', 'Left': 514.0, 'Top': 176.0, 'Height': 32.0, 'Width': 60.0}], 'MaxHeight': 32.0, 'MinTop': 176.0}, {'LineText': '2,590', 'Words': [{'WordText': '2,590', 'Left': 510.0, 'Top': 206.0, 'Height': 30.0, 'Width': 64.0}], 'MaxHeight': 30.0, 'MinTop': 206.0}, {'LineText': '1,120', 'Words': [{'WordText': '1,120', 'Left': 510.0, 'Top': 236.0, 'Height': 32.0, 'Width': 62.0}], 'MaxHeight': 32.0, 'MinTop': 236.0}, {'LineText': '3,850', 'Words': [{'WordText': '3,850', 'Left': 510.0, 'Top': 268.0, 'Height': 30.0, 'Width': 62.0}], 'MaxHeight': 30.0, 'MinTop': 268.0}, {'LineText': '6,980', 'Words': [{'WordText': '6,980', 'Left': 508.0, 'Top': 298.0, 'Height': 31.0, 'Width': 64.0}], 'MaxHeight': 31.0, 'MinTop': 298.0}, {'LineText': '19,800', 'Words': [{'WordText': '19,800', 'Left': 496.0, 'Top': 330.0, 'Height': 31.0, 'Width': 78.0}], 'MaxHeight': 31.0, 'MinTop': 330.0}, {'LineText': '500', 'Words': [{'WordText': '500', 'Left': 528.0, 'Top': 360.0, 'Height': 24.0, 'Width': 40.0}], 'MaxHeight': 24.0, 'MinTop': 360.0}, {'LineText': '14,720', 'Words': [{'WordText': '14,720', 'Left': 494.0, 'Top': 390.0, 'Height': 30.0, 'Width': 74.0}], 'MaxHeight': 30.0, 'MinTop': 390.0}, {'LineText': '5,980', 'Words': [{'WordText': '5,980', 'Left': 502.0, 'Top': 418.0, 'Height': 30.0, 'Width': 62.0}], 'MaxHeight': 30.0, 'MinTop': 418.0}, {'LineText': '1,580', 'Words': [{'WordText': '1,580', 'Left': 502.0, 'Top': 448.0, 'Height': 30.0, 'Width': 62.0}], 'MaxHeight': 30.0, 'MinTop': 448.0}, {'LineText': '3,980', 'Words': [{'WordText': '3,980', 'Left': 498.0, 'Top': 476.0, 'Height': 28.0, 'Width': 64.0}], 'MaxHeight': 28.0, 'MinTop': 476.0}, {'LineText': '1,980', 'Words': [{'WordText': '1,980', 'Left': 498.0, 'Top': 508.0, 'Height': 26.0, 'Width': 58.0}], 'MaxHeight': 26.0, 'MinTop': 508.0}, {'LineText': '4,580', 'Words': [{'WordText': '4,580', 'Left': 494.0, 'Top': 532.0, 'Height': 28.0, 'Width': 62.0}], 'MaxHeight': 28.0, 'MinTop': 532.0}, {'LineText': '1,960', 'Words': [{'WordText': '1,960', 'Left': 494.0, 'Top': 560.0, 'Height': 26.0, 'Width': 58.0}], 'MaxHeight': 26.0, 'MinTop': 560.0}, {'LineText': '2,250', 'Words': [{'WordText': '2,250', 'Left': 492.0, 'Top': 584.0, 'Height': 29.0, 'Width': 60.0}], 'MaxHeight': 29.0, 'MinTop': 584.0}, {'LineText': '27,960', 'Words': [{'WordText': '27,960', 'Left': 480.0, 'Top': 612.0, 'Height': 30.0, 'Width': 70.0}], 'MaxHeight': 30.0, 'MinTop': 612.0}, {'LineText': '41,445', 'Words': [{'WordText': '41,445', 'Left': 482.0, 'Top': 640.0, 'Height': 33.0, 'Width': 68.0}], 'MaxHeight': 33.0, 'MinTop': 640.0}, {'LineText': '4,145', 'Words': [{'WordText': '4,145', 'Left': 494.0, 'Top': 670.0, 'Height': 32.0, 'Width': 58.0}], 'MaxHeight': 32.0, 'MinTop': 670.0}, {'LineText': '73,550', 'Words': [{'WordText': '73,550', 'Left': 484.0, 'Top': 699.0, 'Height': 33.0, 'Width': 72.0}], 'MaxHeight': 33.0, 'MinTop': 699.0}, {'LineText': '73,550', 'Words': [{'WordText': '73,550', 'Left': 486.0, 'Top': 732.0, 'Height': 30.0, 'Width': 72.0}], 'MaxHeight': 30.0, 'MinTop': 732.0}], 'HasOverlay': True}, 'TextOrientation': '0', 'FileParseExitCode': 1, 'ParsedText': '영수증 미지참시 교환/환불 불가\t\r\n※ 정상상품에 한함, 30일 이내(신설 7일)\t\r\n교환/환불 구매점에서 가능(결제카드지참)\t\r\n[구 매]2017-06-02 21:13\tPOS: 1021-5338\t\r\n상품 명\t단•가\t수량\t금\t액\t\r\n01* 노브랜드 굿밀크우\t1,680\t1\t1,680\t\r\n02\t스마트알뜰양복커버\t2,590\t2,590\t\r\n03\t농심 포스틱 84g\t1,120\t1\t1,120\t\r\n04\t농심 올리브짜파게\t3,850\t1\t3,850\t\r\n05*\t산딸기 500g/박스\t6,980\t1\t6,980\t\r\n06\t(G)서핑여워터슈NY\t19,800\t1\t19,800\t\r\n07\t대여용부직포쇼핑백\t500\t1\t500\t\r\n08*\t호주곡물오이스터블\t14,720\t1\t14,720\t\r\n09\t오뚜기 콤비네이션\t5,980\t1\t5,980\t\r\n10\t• 꼬깔콘허니버터 132G\t1,580\t1\t1,580\t\r\nCJ미니드레싱골라담\t5, 900\t1\t3,980\t\r\n12\t청정원허브맛솔트(\t1,980\t1\t1,980\t\r\n13*\t태국미니아스파라거\t4,580\t1\t4,580\t\r\n14\t. 롯데 수박바젤리 56\t980\t2\t1,960\t\r\n15\t바리스타 쇼콜라 32\t2,250\t1\t2,250\t\r\n(*)면 세\t[ 물품\t27,960\t\r\n과세 물품\t41,445\t\r\n. 부가 세\t4,145\t\r\n합\t계\t73,550\t\r\n결제 대상 금액\t73,550\t\r\n', 'ErrorMessage': '', 'ErrorDetails': ''}], 'OCRExitCode': 1, 'IsErroredOnProcessing': False, 'ProcessingTimeInMilliseconds': '1578', 'SearchablePDFURL': 'Searchable PDF not generated as it was not requested.'}

@pytest.mark.asyncio
async def test_extract_items_from_ocr_1():
    result = extract_items_from_ocr(test_data_1)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "이가탄에프캡슐" in result[0]["name"]
    assert result[0]["price"] == 27000
    assert result[0]["quantity"] == 1
    assert result[0]["total"] == 27000

@pytest.mark.asyncio
async def test_extract_items_from_ocr_2():
    result = extract_items_from_ocr(test_data_2)
    print(result)

    assert isinstance(result, list)
    assert len(result) > 0

    assert "노브랜드 굿밀크우" in result[0]["name"]
    assert "오뚜기 콤비네이션" in result[8]["name"]
    assert "롯데 수박바젤리" in result[13]["name"]
    assert result[0]["quantity"] == 1
    assert result[8]["quantity"] == 1
    assert result[13]["quantity"] == 2
    assert result[0]["price"] == 1680
    assert result[8]["price"] == 5980
    assert result[13]["price"] == 980
    assert result[0]["total"] == 1680
    assert result[8]["total"] == 5980
    assert result[13]["total"] == 1960
