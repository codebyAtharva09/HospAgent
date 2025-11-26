import React from 'react';

const ForecastCard = ({ forecastData }) => {
    if (!forecastData) return <div className="animate-pulse bg-white h-48 rounded-xl"></div>;

    const maxVal = Math.max(...forecastData.map(d => d.total_patients));

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <h3 className="text-lg font-bold text-[#111827] mb-4">7-Day Patient Forecast</h3>

            <div className="flex items-end justify-between h-40 space-x-2">
                {forecastData.map((day, idx) => (
                    <div key={idx} className="flex flex-col items-center flex-1 group relative">

                        {/* Tooltip */}
                        <div className="absolute bottom-full mb-2 hidden group-hover:block bg-slate-800 text-white text-xs p-2 rounded z-10 w-32 text-center">
                            <p className="font-bold">{day.date}</p>
                            <p>Total: {day.total_patients}</p>
                            <p>Resp: {day.breakdown.respiratory}</p>
                        </div>

                        <div
                            className="w-full bg-[#769DD7] rounded-t-md transition-all duration-300 hover:bg-[#5a8bc9]"
                            style={{ height: `${(day.total_patients / maxVal) * 100}%` }}
                        ></div>
                        <p className="text-[10px] text-slate-400 mt-2 rotate-0 truncate w-full text-center">
                            {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                        </p>
                    </div>
                ))}
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-3 rounded-lg">
                    <p className="text-xs text-slate-500">Peak Load</p>
                    <p className="text-lg font-bold text-[#111827]">{maxVal} <span className="text-xs font-normal">patients</span></p>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg">
                    <p className="text-xs text-slate-500">Avg Respiratory</p>
                    <p className="text-lg font-bold text-[#111827]">
                        {Math.round(forecastData.reduce((acc, curr) => acc + curr.breakdown.respiratory, 0) / forecastData.length)}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ForecastCard;
