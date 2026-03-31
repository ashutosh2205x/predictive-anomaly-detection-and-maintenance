import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const API = "http://localhost:8000";

function App() {
  const [data, setData] = useState([]);
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const historyRes = await axios.get(`${API}/history`);
        setData(historyRes.data);

        const nextRes = await axios.get(`${API}/next`);
        setLatest(nextRes.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);

    return () => clearInterval(interval);
  }, []);
  const getStatusColor = (severity) => {
    if (severity === "critical") return "#ff4d4f";
    if (severity === "warning") return "#faad14";
    return "#52c41a";
  };

  const getTrendArrow = (slope) => {
    if (!slope) return "—";

    if (slope > 0.5) return "📈 Increasing";
    if (slope < -0.5) return "📉 Decreasing";

    return "➡️ Stable";
  };

  const getRiskColor = (risk) => {
    if (risk === "high") return "#ff4d4f";
    if (risk === "medium") return "#faad14";
    return "#52c41a";
  };

  const chartData = [...data];

  if (latest?.prediction?.next_temp) {
    chartData.push({
      temperature: latest.prediction.next_temp,
      predicted: true,
    });
  }

  if (latest?.prediction?.forecast) {
    latest.prediction.forecast.forEach((temp, i) => {
      chartData.push({
        temperature: temp,
        future: true,
        index: data.length + i,
      });
    });
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>⚙️ Predictive Maintenance</h1>

      {latest && (
        <>
          {/* STATUS CARD */}
          <div
            style={{
              ...styles.card,
              borderLeft: `8px solid ${getStatusColor(latest.severity)}`,
            }}
          >
            <h2>Status: {latest.severity}</h2>
            <p style={styles.metric}>🌡 {latest.temperature} °C</p>
            <p style={styles.sub}>
              Last updated: {new Date().toLocaleTimeString()}
            </p>
          </div>

          {/* GRID */}
          <div style={styles.grid}>
            {/* CHART */}
            <div style={styles.card}>
              <h3>📈 Temperature Trend</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" hide />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="temperature"
                    stroke="#1890ff"
                    strokeWidth={2}
                    dot={(props) => {
                      if (props.payload.predicted) {
                        return (
                          <circle
                            cx={props.cx}
                            cy={props.cy}
                            r={6}
                            fill="red"
                          />
                        );
                      }
                      return null;
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="future"
                    stroke="#ff4d4f"
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* PREDICTION */}
            <div style={styles.card}>
              <h3>🔮 Future Prediction</h3>

              <p style={styles.metric}>
                Next Temp: {latest.prediction?.next_temp ?? "--"} °C
              </p>

              <p style={{ color: getRiskColor(latest.prediction?.risk) }}>
                Risk: {latest.prediction?.risk ?? "--"}
              </p>

              <p style={styles.metric}>
                Trend: {getTrendArrow(latest.prediction?.slope)}
              </p>

              <p style={styles.metric}>
                Confidence: {Math.abs(latest.score || 0).toFixed(3)}
              </p>

              <p>
                {latest.anomaly === -1 ? "🚨 Anomaly Detected" : "✅ Normal"}
              </p>
            </div>
          </div>

          {/* AI EXPLANATION */}
          <div style={styles.card}>
            <h3>🧠 AI Explanation</h3>
            <p style={styles.explanation}>{latest.explanation}</p>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: "30px",
    fontFamily: "Inter, sans-serif",
    background: "#f0f2f5",
    minHeight: "100vh",
  },
  title: {
    marginBottom: "20px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "2fr 1fr",
    gap: "20px",
    marginTop: "20px",
  },
  card: {
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  },
  metric: {
    fontSize: "18px",
    fontWeight: "600",
  },
  sub: {
    fontSize: "12px",
    color: "#888",
  },
  explanation: {
    whiteSpace: "pre-line",
    lineHeight: "1.6",
  },
};

export default App;
