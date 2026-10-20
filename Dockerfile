FROM python:3.13.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system --gid 10001 ledger && adduser --system --uid 10001 --ingroup ledger ledger
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY energy_ledger ./energy_ledger
COPY migrations ./migrations
USER 10001:10001
EXPOSE 8099
CMD ["uvicorn", "energy_ledger.api:app", "--host", "0.0.0.0", "--port", "8099", "--no-access-log"]
