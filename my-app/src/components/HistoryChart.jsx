import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  TimeScale,
  Title,
  Tooltip,
  Legend
);

export default function HistoryChart({ fromTime, toTime, setFromTime, setToTime, fetchHistory, chartData }) {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Sensor History</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-xl mb-4">
        <div>
          <label className="block text-gray-700">From:</label>
          <input
            type="datetime-local"
            value={fromTime}
            onChange={e => setFromTime(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border rounded"
          />
        </div>
        <div>
          <label className="block text-gray-700">To:</label>
          <input
            type="datetime-local"
            value={toTime}
            onChange={e => setToTime(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border rounded"
          />
        </div>
        <div className="md:col-span-2 text-right">
          <button onClick={fetchHistory} className="mt-2 bg-blue-600 text-white px-6 py-2 rounded">
            Load History
          </button>
        </div>
      </div>

      {chartData ? (
        <div className="bg-white p-4 rounded shadow overflow-auto">
          <Line
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: {
                  type: 'time',
                  time: { unit: 'hour' },
                  title: { display: true, text: 'Time' },
                },
                y: {
                  beginAtZero: true,
                  title: { display: true, text: 'Values' },
                },
              },
            }}
            height={400}
          />
        </div>
      ) : (
        <p className="text-gray-500">Select a time range and click "Load History".</p>
      )}
    </div>
  );
}
