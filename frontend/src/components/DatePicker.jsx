import { useState } from 'react';
import CloseButton from './CloseButton';

function buildCalendar(year, month) {
    const first = new Date(year, month, 1).getDay();
    const days = new Date(year, month + 1, 0).getDate();
    const offset = (first + 6) % 7; // Mon-start
    return { days, offset };
}

export default function DatePicker({ validDateRanges, rawDate, setRawDate, onOpenChange }) {
    const allValid = new Set(
        validDateRanges.flatMap(([a, b]) => {
            const dates = [];
            const cur = new Date(a);
            const end = new Date(b);
            while (cur <= end) {
                dates.push(cur.toISOString().slice(0, 10));
                cur.setDate(cur.getDate() + 1);
            }
            return dates;
        })
    );

    const latestDate = validDateRanges.at(-1)?.at(-1);
    const displayDate = rawDate === 'latest' ? latestDate : rawDate;

    const initial = displayDate ? new Date(displayDate) : new Date();
    const [open, setOpen] = useState(false);
    const setOpenWithCb = (v) => { setOpen(v); onOpenChange?.(v); };
    const [year, setYear] = useState(initial.getFullYear());
    const [month, setMonth] = useState(initial.getMonth());
    const { days, offset } = buildCalendar(year, month);
    const cells = Array(offset).fill(null).concat(Array.from({ length: days }, (_, i) => i + 1));

    const pad = (n) => String(n).padStart(2, '0');
    const toISO = (d) => `${year}-${pad(month + 1)}-${pad(d)}`;

    const prevMonth = () => { if (month === 0) { setMonth(11); setYear(y => y - 1); } else setMonth(m => m - 1); };
    const nextMonth = () => { if (month === 11) { setMonth(0); setYear(y => y + 1); } else setMonth(m => m + 1); };

    return (
        <>
            <button
                onClick={() => setOpenWithCb(true)}
                style={{ padding: '2px 8px', background: '#fff', border: '1px solid #9ca3af' }}
            >
                {rawDate}
            </button>
            {open && (
                <div className="item_popup" onClick={() => setOpenWithCb(false)}>
                    <div className="item_popup_inner2" onClick={(event) => event.stopPropagation()}>
                        <div className="max-w-7xl mx-auto w-full h-full flex flex-col">
                            <div className="flex-none flex flex-row justify-end"><CloseButton size={35} style={{"marginBottom":"0.5em"}} onClick={() => setOpenWithCb(false)} /></div>
                            <div className="grow overflow-auto min-h-0">
                                <div style={{ minWidth: '22em' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 11 }}>
                                        <button onClick={prevMonth} style={{ cursor: 'pointer', padding: '0 9px', fontSize: 20 }}>‹</button>
                                        <span style={{ fontWeight: 600, fontSize: 15 }}>
                                            {new Date(year, month).toLocaleString('default', { month: 'long', year: 'numeric' })}
                                        </span>
                                        <button onClick={nextMonth} style={{ cursor: 'pointer', padding: '0 9px', fontSize: 20 }}>›</button>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, textAlign: 'center' }}>
                                        {['Mo','Tu','We','Th','Fr','Sa','Su'].map(d => (
                                            <div key={d} style={{ fontSize: 12, color: '#6b7280', fontWeight: 600, paddingBottom: 5 }}>{d}</div>
                                        ))}
                                        {cells.map((d, i) => {
                                            if (!d) return <div key={i} />;
                                            const iso = toISO(d);
                                            const isValid = allValid.has(iso);
                                            const isSelected = iso === rawDate;
                                            return (
                                                <button
                                                    key={i}
                                                    disabled={!isValid}
                                                    onClick={() => { setRawDate(iso); setOpenWithCb(false); }}
                                                    style={{
                                                        fontSize: 13, padding: '5px 0', borderRadius: 4, border: 'none',
                                                        cursor: isValid ? 'pointer' : 'default',
                                                        background: isSelected ? '#3b82f6' : isValid ? '#dbeafe' : 'transparent',
                                                        color: isSelected ? '#fff' : isValid ? '#1d4ed8' : '#d1d5db',
                                                        fontWeight: isSelected ? 700 : 400,
                                                    }}
                                                >
                                                    {d}
                                                </button>
                                            );
                                        })}
                                    </div>
                                    <div style={{ marginTop: 11, borderTop: '1px solid #e5e7eb', paddingTop: 9 }}>
                                        <button
                                            onClick={() => { setRawDate('latest'); setOpenWithCb(false); }}
                                            style={{
                                                width: '100%', padding: '6px 0', borderRadius: 4, border: 'none',
                                                background: rawDate === 'latest' ? '#3b82f6' : '#dbeafe',
                                                color: rawDate === 'latest' ? '#fff' : '#1d4ed8',
                                                cursor: 'pointer', fontSize: 13, fontWeight: 600
                                            }}
                                        >
                                            latest
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
