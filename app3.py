from flask import Flask, request, jsonify, json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import operator
################################collaboration_filtering################################
app3 = Flask(__name__)

@app3.route('/submit_user_input', methods=['POST'])
def submit_user_input():
    # 사용자로부터 입력 받기
    data = request.json

    # 입력값 확인
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 데이터프레임 생성
    user = pd.DataFrame(columns=['user_id', 'type', 'country', 'city'])
    for item in data:
        if isinstance(item, dict):
            name = item.get('name')
            str_num = item.get('num')
            num = int(str_num)
            types = item.get('types')

            for i in range(num):
                country = item.get('country')
                city = item.get('city')

                user = pd.concat([user, pd.DataFrame({'user_id': [name], 'type': [types], 'country': [country], 'city': [city]})], ignore_index=True)
            else:
                # 예외 처리: 문자열인 경우 처리하지 않고 다음 반복으로 넘어감
                continue

    # 생성된 데이터프레임 확인
    print(user)

    # 데이터프레임을 CSV 파일로 저장
    user.to_csv('user_input.csv', encoding='cp949', index=False)
    # return jsonify({'message': 'User input submitted successfully', 'data': user.to_json()})
    return jsonify({'message': 'User input submitted successfully'})

def preprocess_data():
    places = pd.read_csv('places.csv', encoding='cp949')
    user = pd.read_csv('user_input.csv', encoding='cp949')
    # A에만 있는 행 추출
    df_only_A = user[~user['city'].isin(places['city'])]
    # B에 A에만 있는 행 추가
    place = pd.concat([places, df_only_A], ignore_index=True)
    
    # 중복 행 개수 계산
    column = ['country', 'city']
    duplicates = place.duplicated(subset=column)
    counts = place[duplicates].groupby(['country', 'city']).size() + 1

    # 중복 행 삭제
    place.drop_duplicates(subset=column, keep='first', inplace=True)
    place.rename(columns={'Unnamed: 4': 'counts'}, inplace=True)

    # 카테고리를 숫자로 변환 - places
    categories = ['모험가형', '문화 체험형', '휴양형', '음식 여행형', '자유 여행형', '문화 예술형']
    place['EncodedCategory'] = pd.factorize(place['type'])[0] + 1

    # 나라를 숫자로 변환 - places
    place['c_to_n'] = pd.factorize(place['country'])[0]
    factorized_values = pd.factorize(place['c_to_n'])[0]
    unique_categories = place['country']
    converted_values = [unique_categories[index] for index in factorized_values]
    place['n_to_c'] = converted_values
    
    # 카테고리를 숫자로 변환 - user
    user['EncodedCategory'] = pd.factorize(user['type'])[0] + 1

    # 나라를 숫자로 변환 - user
    user['c_to_n'] = pd.factorize(user['country'])[0]
    factorized_values = pd.factorize(user['c_to_n'])[0]
    unique_categories = user['country']
    converted_values = [unique_categories[index] for index in factorized_values]
    user['n_to_c'] = converted_values
    print(user)

    return places, user

# 비슷한 성향의 유저 찾기 함수
def find_similar_users(user_matrix, place_matrix, k):
    user = user_matrix
    other_users = place_matrix

    u_country = user['country'].iloc[0]
    u_city = user['city'].iloc[0]

    similarities = []
    for index, row in other_users.iterrows():
        o_country = row['country']
        o_city = row['city']
        similarity = 1 if u_country == o_country and u_city == o_city else 0
        similarities.append(similarity)

    other_users['similarity'] = similarities
    top_users = other_users.sort_values('similarity', ascending=False).head(k)

    user_countries = top_users['country'].tolist()
    user_cities = top_users['city'].tolist()

    return user_countries, user_cities

@app3.route('/get_similar_users', methods=['POST'])
def get_similar_users():
    data = request.json
    k = data.get('k')
    place, user = preprocess_data()
    
    similar_users = find_similar_users(user, place, k)

    # user_countries = places.loc[similar_users, 'country'].tolist()
    # user_cities = places.loc[similar_users, 'city'].tolist()

    return jsonify({'message': 'User input submitted successfully'})
    # return jsonify({'user_countries': user_countries, 'user_cities': user_cities})

if __name__ == '__main__':
    app3.run()
