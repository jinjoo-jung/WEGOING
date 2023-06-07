from flask import Flask, request, jsonify, json
import pandas as pd
import ast as ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route("/", methods=["POST"])
def process_data():
    dataAll = request.json.get("data")
    print(dataAll)

    # 여행지 이름만 추출하기
    dataNeed = (dataAll["travelPastName"])
    print(dataNeed)
    
    travel = pd.read_csv('Travel.csv', encoding='UTF-8')

    # 컬럼 추출 (관광 자원, 여행지)
    data =travel[['관광 자원', '여행지']]
    data[['관광 자원','여행지']].head()
    
    counter_vector = CountVectorizer(ngram_range=(1,3))
    c_vector_관광자원=counter_vector.fit_transform(data['관광 자원'])
    similarity_관광자원 = cosine_similarity(c_vector_관광자원,c_vector_관광자원 ).argsort()[:,::-1]
    
    def recommend_travel_list(df, 여행지, top =2):
       target_travel_index = df[df['여행지']==여행지].index.values
       sim_index = similarity_관광자원[target_travel_index,:top].reshape(-1)
       sim_index = sim_index[sim_index!=target_travel_index]
       result = df.iloc[sim_index]
       return result
    
    output= recommend_travel_list(data, 여행지=dataNeed)
    
    json_output=output.to_json(orient='records')
    print(json_output)

    return jsonify(json_output)


