FROM python:3.10-slim
RUN ln -s /usr/bin/python3 /usr/bin/python
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt
EXPOSE 8000
CMD ["python", "main.py"]

# opik configure
# P4DaWMUR0FdNDZBuRzKxS7v2K
# RUN guardrails configure --token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNTEwNTc0NTE1OTkwMzQ1MTc3NiIsImFwaUtleUlkIjoiOWRhNzhlYWYtZjY4OS00NDU4LThhNmUtNThmYzdiMTY5MDRkIiwic2NvcGUiOiJyZWFkOnBhY2thZ2VzIiwicGVybWlzc2lvbnMiOltdLCJpYXQiOjE3MzYzMDk1NjMsImV4cCI6NDg4OTkwOTU2M30.ZdNGEk-p8VWheu2bD9xcjwrcX36jPS7vwBnc_u-QZqc
# RUN guardrails hub install hub://guardrails/gibberish_text
# RUN guardrails hub install hub://guardrails/toxic_language