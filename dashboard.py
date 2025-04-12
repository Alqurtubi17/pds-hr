import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests, tempfile
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
import joblib

# Set page config
st.set_page_config(page_title="HR Attrition Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("https://raw.githubusercontent.com/dicodingacademy/dicoding_dataset/refs/heads/main/employee/employee_data.csv")

# Unduh file dari URL
url = "https://github.com/Alqurtubi17/pds-hr/raw/main/model_pipeline.pkl"
response = requests.get(url)
if response.status_code == 200:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    # Load model
    model, _, selected_features = joblib.load(tmp_file_path)
else:
    raise Exception("Gagal mengunduh file model dari GitHub.")
# Preprocessing
df.dropna(inplace=True)
df.drop(['EmployeeId', 'Over18', 'StandardHours', 'EmployeeCount'], axis=1, inplace=True)
df_corr = df.copy()
df['Attrition'] = df['Attrition'].map({1: 'Yes', 0: 'No'})
education_map = {1: 'Below College', 2: 'College', 3: 'Bachelor', 4: 'Master', 5: 'Doctor'}
worklife_map = {1: 'Low', 2: 'Good', 3: 'Excellent', 4: 'Outstanding'}
satisfaction_map = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very High'}
df['Education'] = df['Education'].map(education_map)
df['WorkLifeBalance'] = df['WorkLifeBalance'].map(worklife_map)
df['JobSatisfaction'] = df['JobSatisfaction'].map(satisfaction_map)
df['EnvironmentSatisfaction'] = df['EnvironmentSatisfaction'].map(satisfaction_map)
df['MaritalStatus'] = df['MaritalStatus'].map({"Single": 0, "Married": 1, "Divorced": 2})
df['OverTime'] = df['OverTime'].map({"No": 0, "Yes": 1})

# Sidebar navigation
page = st.sidebar.selectbox("Pilih Halaman", ["Dashboard", "Prediction"])

if page == "Dashboard":
    st.markdown("<h2 style='text-align:center; margin-top:0px; margin-bottom:30px'>HR Attrition Dashboard</h2>", unsafe_allow_html=True)

    # Metrics
    total_employees = len(df)
    total_attrition = df['Attrition'].value_counts().get('Yes', 0)
    attrition_rate = total_attrition / total_employees * 100
    active_employees = total_employees - total_attrition
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div style='background-color:#FDFAF6; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1); text-align:center;'>" +
                    f"<h5>Total Employees</h5><h3>{total_employees}</h3></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='background-color:#FDFAF6; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1); text-align:center;'>" +
                    f"<h5>Total Attrition</h5><h3>{total_attrition}</h3></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='background-color:#FDFAF6; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1); text-align:center;'>" +
                    f"<h5>Attrition Rate</h5><h3>{attrition_rate:.2f}%</h3></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div style='background-color:#FDFAF6; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1); text-align:center;'>" +
                    f"<h5>Active Employees</h5><h3>{active_employees}</h3></div>", unsafe_allow_html=True)

    st.markdown("")
    # Feature Importance + Pie Chart
    col_pie, col_feat = st.columns([1, 3])

    with col_feat:
        X = df[['Age', 'MaritalStatus', 'OverTime', 'StockOptionLevel', 'TotalWorkingYears']]
        feat_imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
        fig_feat = px.bar(
            feat_imp,
            x=feat_imp.index,
            y=feat_imp.values,
            labels={'index': 'Feature', 'y': 'Importance'},
            title="Key Factors Contributing to High Attrition Rate",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_feat.update_traces(textposition='outside')
        fig_feat.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            title=dict(x=0.3),
            showlegend=False
        )
        st.plotly_chart(fig_feat, use_container_width=True)

    with col_pie:
        pie_data = df['Attrition'].value_counts().reset_index()
        pie_data.columns = ['Attrition', 'Count']
        fig_pie = px.pie(pie_data, names='Attrition', values='Count', title="Attrition Ratio", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            title=dict(x=0.3))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<h6 style='text-align:center;'>Attrition Comparison by Categorical Features</h6>", unsafe_allow_html=True)
    fig_cat = make_subplots(rows=2, cols=4, subplot_titles=('WorkLifeBalance', 'Department', 'EducationField', 'MaritalStatus', 'JobRole', 
                            'Gender', 'EnvironmentSatisfaction','JobSatisfaction'))
    categorical_features = ['WorkLifeBalance', 'Department', 'EducationField', 'MaritalStatus', 'JobRole', 
                            'Gender', 'EnvironmentSatisfaction','JobSatisfaction']
    for idx, col in enumerate(categorical_features):
        row = idx // 4 + 1
        column = idx % 4 + 1
        
        # Hitung rasio attrition Yes per kategori
        grouped = df.groupby([col, 'Attrition']).size().reset_index(name='Count')
        total_per_group = grouped.groupby(col)['Count'].transform('sum')
        grouped['Ratio'] = grouped['Count'] / total_per_group * 100

        yes_df = grouped[grouped['Attrition'] == 'Yes'].sort_values(by='Ratio', ascending=False)
        
        fig_cat.add_trace(
            go.Bar(
                x=yes_df[col],
                y=yes_df['Ratio'],
                name='Attrition Yes',
                text=yes_df['Ratio'].round(1).astype(str) + '%',
                textposition='auto',
                marker_color=px.colors.qualitative.Pastel
            ),
            row=row, col=column
        )
        
        fig_cat.update_xaxes(showgrid=False, row=row, col=column)
        fig_cat.update_yaxes(title_text='%', showgrid=False, row=row, col=column)

    fig_cat.update_layout(
        height=650,
        width=1400,
        showlegend=False,
        margin=dict(t=50),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    col1, col2 = st.columns([1, 1.5])
    with col1:
        relevant_numerics = [
            'Age', 'DailyRate', 'DistanceFromHome', 'HourlyRate', 'MonthlyIncome',
            'MonthlyRate', 'NumCompaniesWorked', 'PercentSalaryHike',
            'TotalWorkingYears', 'TrainingTimesLastYear', 'YearsAtCompany',
            'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager']
        
        st.markdown("<h6 style='text-align:center;'>Key HR-Related Variable Analysis</h6>", unsafe_allow_html=True)
        selected = st.selectbox("Select Variable", relevant_numerics)
        
        fig = px.violin(df, y=selected, x='Attrition', box=True, points='all',
                        color='Attrition', color_discrete_sequence=px.colors.qualitative.Pastel)
        
        fig.update_layout(
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        # Correlation Heatmap
        st.markdown("<h6 style='text-align:center; font-size:18px;'>🔗 Correlation between Numerical Features</h6>", unsafe_allow_html=True)

        # Hitung korelasi numerik terhadap Attrition
        corr_series = df_corr[[
            'Age', 'DailyRate', 'DistanceFromHome', 'HourlyRate', 'MonthlyIncome',
            'MonthlyRate', 'NumCompaniesWorked', 'PercentSalaryHike',
            'TotalWorkingYears', 'TrainingTimesLastYear', 'YearsAtCompany',
            'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager'
        ]].corrwith(df_corr['Attrition']).sort_values(key=lambda x: abs(x), ascending=True)

        # Buat bar chart horizontal
        fig_corr_bar = px.bar(
            x=corr_series.values,
            y=corr_series.index,
            orientation='h',
            text=corr_series.round(2),
            color=corr_series.values,
            color_continuous_scale=px.colors.qualitative.Pastel,
            labels={'x': 'Correlation', 'y': 'Feature'}
        )

        fig_corr_bar.update_layout(
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig_corr_bar, use_container_width=True)

    st.markdown("<h5 style='text-align:center;'> Employee Productivity by Department and Job Role</h5>", unsafe_allow_html=True)

    fig = px.treemap(
        df_corr,
        path=['Department', 'JobRole'],
        values='JobInvolvement',
        color='JobSatisfaction',
        color_continuous_scale=px.colors.qualitative.Pastel,
        hover_data=['JobInvolvement', 'JobSatisfaction'],
        hover_name='JobRole'
    )

    fig.update_layout(
        font_family='Open Sans',
        font_size=14,
        margin=dict(l=20, r=20, t=50, b=20),
        height = 650
    )

    fig.update_traces(
        hovertemplate='<b>Department</b>: %{label}<br>'
                    '<b>Job Role</b>: %{hovertext}<br>'
                    '<b>Job Involvement</b>: %{customdata[0]}'
    )

    st.plotly_chart(fig, use_container_width=True)

# ==== Halaman Prediksi ====
elif page == "Prediction":
    st.title("🔮 Predict Employee Attrition")

    # Input dari pengguna
    age = st.number_input("Age", min_value=18, max_value=60, value=30)
    marital = st.selectbox("Marital Status", options=["Single", "Married", "Divorced"])
    overtime = st.selectbox("OverTime", options=["No", "Yes"])
    stock = st.selectbox("Stock Option Level", options=[0, 1, 2, 3])
    total_years = st.number_input("Total Working Years", min_value=0, max_value=40, value=5)

    # Mapping input
    marital_encoded = {"Single": 0, "Married": 1, "Divorced": 2}[marital]
    overtime_encoded = {"No": 0, "Yes": 1}[overtime]

    if st.button("Predict"):
        try:
            # Bangun dataframe input
            input_df = pd.DataFrame([[age, marital_encoded, overtime_encoded, stock, total_years]],
                                    columns=selected_features)

            # Scaling manual berdasarkan data asli
            scaler = MinMaxScaler()
            df_selected = df[selected_features]
            scaler.fit(df_selected)
            input_scaled = scaler.transform(input_df)

            # Prediksi
            pred = model.predict(input_scaled)[0]
            prob = model.predict_proba(input_scaled)[0][1]

            # Output
            st.success(f"Prediction: {'Attrition' if pred == 1 else 'No Attrition'} (Probability: {prob:.2%})")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat prediksi: {e}")