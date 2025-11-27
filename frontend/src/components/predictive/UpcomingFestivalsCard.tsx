import React, { useState, useMemo } from 'react';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, isToday, parseISO } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';

export interface FestivalEvent {
    id: string;
    name: string;
    date: string; // YYYY-MM-DD
    risk_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
}

interface Props {
    events: FestivalEvent[];
}

const UpcomingFestivalsCard: React.FC<Props> = ({ events = [] }) => {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [selectedDate, setSelectedDate] = useState<Date | null>(null);

    // Generate calendar days
    const calendarDays = useMemo(() => {
        const monthStart = startOfMonth(currentMonth);
        const monthEnd = endOfMonth(monthStart);
        const startDate = startOfWeek(monthStart);
        const endDate = endOfWeek(monthEnd);

        return eachDayOfInterval({ start: startDate, end: endDate });
    }, [currentMonth]);

    // Filter events for the list
    const filteredEvents = useMemo(() => {
        let filtered = events;

        // Sort by date ascending
        filtered.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        if (selectedDate) {
            filtered = filtered.filter(event => isSameDay(parseISO(event.date), selectedDate));
        } else {
            // Default: show next 60 days if no date selected? 
            // User said: "Default: show all upcoming festivals in the next 30–60 days returned from the backend."
            // The backend returns upcoming festivals, so we just show them.
        }
        return filtered;
    }, [events, selectedDate]);

    // Helper to get events for a specific day
    const getEventsForDay = (day: Date) => {
        return events.filter(event => isSameDay(parseISO(event.date), day));
    };

    // Helper for risk color
    const getRiskColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return 'bg-red-500';
            case 'HIGH': return 'bg-orange-500';
            case 'MODERATE': return 'bg-yellow-500';
            default: return 'bg-blue-400'; // LOW
        }
    };

    const getRiskBadgeColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return 'bg-red-100 text-red-700 border-red-200';
            case 'HIGH': return 'bg-orange-100 text-orange-700 border-orange-200';
            case 'MODERATE': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
            default: return 'bg-blue-50 text-blue-700 border-blue-200';
        }
    };

    const handlePrevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));
    const handleNextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));

    const handleDateClick = (day: Date) => {
        if (selectedDate && isSameDay(day, selectedDate)) {
            setSelectedDate(null); // Deselect
        } else {
            setSelectedDate(day);
        }
    };

    return (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-slate-100 flex items-center gap-2">
                <div className="p-2 bg-indigo-50 rounded-lg">
                    <CalendarIcon className="w-5 h-5 text-indigo-600" />
                </div>
                <h3 className="font-bold text-slate-800">Upcoming Festivals</h3>
            </div>

            {/* Calendar View */}
            <div className="p-4 pb-2">
                <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold text-slate-700">
                        {format(currentMonth, 'MMMM yyyy')}
                    </h4>
                    <div className="flex gap-1">
                        <button onClick={handlePrevMonth} className="p-1 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button onClick={handleNextMonth} className="p-1 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-7 gap-1 text-center mb-2">
                    {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map(day => (
                        <div key={day} className="text-xs font-medium text-slate-400">
                            {day}
                        </div>
                    ))}
                </div>

                <div className="grid grid-cols-7 gap-1">
                    {calendarDays.map((day, idx) => {
                        const dayEvents = getEventsForDay(day);
                        const hasEvents = dayEvents.length > 0;
                        const isSelected = selectedDate && isSameDay(day, selectedDate);
                        const isCurrentMonth = isSameMonth(day, currentMonth);
                        const isTodayDate = isToday(day);

                        // Determine the highest risk for the dot color
                        const maxRisk = dayEvents.reduce((max, e) => {
                            if (e.risk_level === 'CRITICAL') return 3;
                            if (e.risk_level === 'HIGH' && max < 2) return 2;
                            if (e.risk_level === 'MODERATE' && max < 1) return 1;
                            return max;
                        }, 0);

                        let dotColor = 'bg-blue-400';
                        if (maxRisk === 3) dotColor = 'bg-red-500';
                        else if (maxRisk === 2) dotColor = 'bg-orange-500';
                        else if (maxRisk === 1) dotColor = 'bg-yellow-500';

                        return (
                            <button
                                key={idx}
                                onClick={() => handleDateClick(day)}
                                className={`
                                    relative h-8 w-8 mx-auto flex items-center justify-center rounded-full text-xs font-medium transition-all
                                    ${!isCurrentMonth ? 'text-slate-300' : 'text-slate-700'}
                                    ${isSelected ? 'bg-indigo-600 text-white shadow-md' : 'hover:bg-slate-50'}
                                    ${isTodayDate && !isSelected ? 'bg-indigo-50 text-indigo-700 font-bold' : ''}
                                `}
                            >
                                {format(day, 'd')}
                                {hasEvents && (
                                    <span className={`absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full ${isSelected ? 'bg-white' : dotColor}`}></span>
                                )}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-100 mx-4"></div>

            {/* Events List */}
            <div className="flex-1 overflow-y-auto p-4 min-h-[150px]">
                {filteredEvents.length === 0 ? (
                    <div className="text-center py-8 text-slate-400 text-sm">
                        {selectedDate ? "No festivals on this date." : "No upcoming festivals detected."}
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredEvents.map(event => (
                            <div key={event.id} className="flex items-center justify-between group">
                                <div>
                                    <p className="font-semibold text-slate-700 text-sm group-hover:text-indigo-600 transition-colors">
                                        {event.name}
                                    </p>
                                    <p className="text-xs text-slate-500">
                                        {format(parseISO(event.date), 'dd MMM yyyy')}
                                    </p>
                                </div>
                                <span className={`px-2 py-1 rounded-md text-[10px] font-bold border uppercase tracking-wide ${getRiskBadgeColor(event.risk_level)}`}>
                                    {event.risk_level}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-3 bg-slate-50 border-t border-slate-100 text-[10px] text-slate-400 text-center">
                Synced with Google Calendar
            </div>
        </div>
    );
};

export default UpcomingFestivalsCard;
