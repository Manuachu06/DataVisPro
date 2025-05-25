from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

df_global = None
uploaded_filename = None

@app.route('/')
def landing():
    # Render the landing page
    return render_template('landing.html')


@app.route('/app', methods=['GET', 'POST'])
def index():
    global df_global, uploaded_filename

    chart_html = None
    message = None

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                message = 'No file selected.'
            else:
                uploaded_filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(uploaded_filename)
                df_global = pd.read_excel(uploaded_filename)
                df_global = df_global.head(500)
                message = f'File "{file.filename}" uploaded successfully. Columns detected: {len(df_global.columns)}'

        elif 'chart_type' in request.form:
            if df_global is None:
                message = "Please upload an Excel file first."
            else:
                chart_type = request.form.get('chart_type')
                x_col = request.form.get('x_column')
                y_cols = request.form.getlist('y_columns')

                if not x_col or not y_cols:
                    message = "Please select X and Y columns."
                else:
                    try:
                        if chart_type == 'Pie':
                            fig = px.pie(df_global, names=x_col, values=y_cols[0])
                        elif chart_type == 'Heatmap':
                            sub_df = df_global[y_cols].select_dtypes(include='number')
                            corr = sub_df.corr()
                            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
                        else:
                            df_melt = df_global[[x_col] + y_cols]
                            df_long = df_melt.melt(id_vars=[x_col], value_vars=y_cols,
                                                   var_name='Variable', value_name='Value')

                            if chart_type == 'Line':
                                fig = px.line(df_long, x=x_col, y='Value', color='Variable', title="Line Chart")
                            elif chart_type == 'Bar':
                                fig = px.bar(df_long, x=x_col, y='Value', color='Variable',
                                             barmode='group', title="Bar Chart")
                            elif chart_type == 'Scatter':
                                fig = px.scatter(df_global, x=x_col, y=y_cols[0], title="Scatter Plot")
                            elif chart_type == 'Histogram':
                                fig = px.histogram(df_global, x=y_cols[0], title="Histogram")
                            elif chart_type == 'Box':
                                fig = px.box(df_long, x=x_col, y='Value', color='Variable', title="Box Plot")
                            elif chart_type == 'Area':
                                fig = px.area(df_long, x=x_col, y='Value', color='Variable', title="Area Chart")
                            elif chart_type == 'Violin':
                                fig = px.violin(df_long, x=x_col, y='Value', color='Variable', box=True, points='all', title="Violin Plot")
                            else:
                                message = "Unsupported chart type."
                                fig = None

                        if fig:
                            chart_html = fig.to_html(full_html=False)
                    except Exception as e:
                        message = f"Error generating chart: {e}"

    if df_global is not None:
        columns = df_global.columns.tolist()
        numeric_columns = df_global.columns.tolist()
    else:
        columns = []
        numeric_columns = []

    return render_template('index.html',
                           columns=columns,
                           numeric_columns=numeric_columns,
                           chart=chart_html,
                           message=message)


if __name__ == '__main__':
    app.run(debug=True)
