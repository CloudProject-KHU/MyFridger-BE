import re

def extract_items_from_ocr(json_data, threshold_x=150, threshold_y=16):
    """
    OCR Response로 부터 영수증 항목을 분리하는 함수 입니다.
    :param json_data: OCR API Response
    :param threshold: 같은 행으로 간주할 텍스트의 y좌표 오차 범위 (픽셀)
    :return: 추출된 항목들의 리스트
    """

    # 데이터 전처리
    try:
        parsed_result = json_data['ParsedResults'][0]
        if 'TextOverlay' in parsed_result:
            lines_data = parsed_result['TextOverlay']['Lines']
        elif 'Overlay' in parsed_result:
            lines_data = parsed_result['Overlay']['Lines']
        else:
            return "JSON에 텍스트 데이터(Overlay/TextOverlay)가 없습니다."
    except (KeyError, IndexError, TypeError):
        return "데이터 형식이 올바르지 않습니다."

    # 단어 추출 및 Y축 정렬
    all_words = []
    for line in lines_data:
        all_words.extend(line["Words"])
    all_words.sort(key=lambda x: x["Top"])

    if not all_words: return "텍스트 데이터가 없습니다."

    # 행 분리
    rows = []
    current_row = [all_words[0]]

    for word in all_words[1:]:
        # 현재 y가 이전 평균과 가까우면 같은 행으로 간주
        prev_avg_top = sum([w["Top"] for w in current_row]) / len(current_row)
        if abs(word["Top"] - prev_avg_top) <= threshold_y:
            current_row.append(word)
        else:
            rows.append(current_row)
            current_row = [word]
    rows.append(current_row)

    for row in rows:
        row.sort(key=lambda x: x["Left"])

    # 헤더 탐색
    column_map = {"price": None, "quantity": None, "total_price": None}
    KEYWORDS = {
        "price": ["단가", "가격"],
        "quantity": ["수량", "개수"],
        "total_price": ["금액", "합계", "가액"],
    }
    
    item_start_index = 0
    header_found = False

    for idx, row in enumerate(rows):
        row_text = "".join([w["WordText"] for w in row])
        normalized_text = row_text.replace(" ", "")
        
        # 헤더 키워드 발견 시 좌표 매핑
        if any(k in normalized_text for k in ["상품", "품명", "단가", "수량", "금액"]):
            header_found = True
            item_start_index = idx + 1
            
            for word in row:
                w_text = word["WordText"].replace(" ", "")
                w_center = word["Left"] + (word["Width"] / 2)
                for col_type, keywords in KEYWORDS.items():
                    if any(k in w_text for k in keywords):
                        column_map[col_type] = w_center
            break # 첫 번째 헤더 라인만 찾으면 중단
    
    # 헤더를 못찾은 경우 fallback
    if not header_found:
        item_start_index = 0 

    # 실제 항목 추출
    items = []
    current_item = {"name": "", "price": 0, "quantity": 1, "total": 0}

    STOP_KEYWORDS = ["합계", "카드", "부가세", "과세", "면세", "결제", "거스름"]
    
    for row in rows[item_start_index:]:
        row_text = "".join([str(w["WordText"]) for w in row])
        norm_text = row_text.replace(" ", "")

        # 종료 키워드 감지 시 루프 종료
        if any(x in norm_text for x in STOP_KEYWORDS):
            # 마지막 아이템이 있다면 저장 후 종료
            if current_item["price"] > 0 or current_item["total"] > 0:
                 current_item["name"] = current_item["name"].strip()
                 items.append(current_item)
            break
            
        if "----" in row_text: continue

        for word in row:
            raw_text = str(word["WordText"])
            text = raw_text.replace(",", "").replace("원", "")
            center_x = word["Left"] + (word["Width"] / 2)

            if text.isdigit(): # 숫자인 경우
                val = int(text)
                
                # 날짜/시간 필터링 (연도, 월/일, 시간 등)
                if val >= 2000 and val <= 2030: continue
                
                closest_col = None
                
                # case 1. 헤더 좌표 기반 매핑
                if header_found and any(column_map.values()):
                    min_dist = float("inf")
                    for col_type, col_center in column_map.items():
                        if col_center is not None:
                            dist = abs(center_x - col_center)
                            if dist < min_dist:
                                min_dist = dist
                                closest_col = col_type

                    # 오차 범위 벗어나면 매핑 취소
                    if min_dist > threshold_x: 
                        closest_col = None

                # case 2. 값 기반 추론 (헤더가 없거나 매핑 실패 시)
                if closest_col is None:
                    if val <= 100: # 100 이하는 수량으로 추정
                        closest_col = "quantity"
                    else: # 100 초과는 가격으로 추정
                        # 이미 가격이 있으면 합계로 간주, 없으면 단가로 간주
                        if current_item["price"] == 0:
                            closest_col = "price"
                        else:
                            closest_col = "total_price"

                # 값 할당
                if closest_col == "price": current_item["price"] = val
                elif closest_col == "quantity": current_item["quantity"] = val
                elif closest_col == "total_price": current_item["total"] = val

            else: # 텍스트의 경우
                # 유효한 상품명인지 검증. 한글이나 영어 둘중 하나는 적어도 있어야 함
                if re.search(r'[가-힣a-zA-Z]', raw_text):
                     current_item["name"] += raw_text + " "

        # 가격 정보가 채워졌으면 하나의 아이템으로 확정
        if current_item["price"] > 0 or current_item["total"] > 0:
            current_item["name"] = current_item["name"].strip()

            # 수량 0 방지 및 값 보정
            qty = current_item["quantity"] if current_item["quantity"] > 0 else 1
            
            if current_item["total"] == 0 and current_item["price"] > 0:
                current_item["total"] = current_item["price"] * qty
            
            if current_item["price"] == 0 and current_item["total"] > 0:
                current_item["price"] = int(current_item["total"] / qty)
            
            # 최종 업데이트 된 수량 반영
            current_item["quantity"] = qty
            
            items.append(current_item)
            current_item = {"name": "", "price": 0, "quantity": 1, "total": 0}

    return items