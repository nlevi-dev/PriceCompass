import { useState, useMemo } from 'react';
import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

const InteractiveBarChart = ({ data, colors, maxY = 100, onBarEnter = (_) => _, onBarLeave = (_) => _, onBarClick = (_) => _}) => {

    const dataFiltered = useMemo(() => data.filter(d => d.sum > 0), [data]);
    const [activeIndex, setActiveIndex] = useState(null);

    if (dataFiltered.length === 0) {
        return (
            <div style={{ width: '100%', height: '200px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <p style={{ fontSize: '18px', color: '#666' }}>no data to display</p>
            </div>
        );
    }

    const onBarEnter_ = (state, index) => {
        onBarEnter(state.name);
        setActiveIndex(index);
    };

    const onBarLeave_ = () => {
        onBarLeave(null);
        setActiveIndex(null);
    };

    const onBarClick_ = (state) => {
        onBarClick(state.name);
    };

    return (
        <div className="flex justify-center w-full">
            <div style={{ width: '100%', height: '300px' }}>
                <ResponsiveContainer>
                    <BarChart
                        data={dataFiltered}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" tickFormatter={(value) => value.charAt(0)} />
                        <YAxis domain={[0, maxY]} />
                        <Bar
                            dataKey="sum"
                            onMouseEnter={onBarEnter_}
                            onMouseLeave={onBarLeave_}
                            onClick={onBarClick_}
                            isAnimationActive={false}
                            cursor="pointer"
                        >
                            {dataFiltered.map((category, index) => (
                                <Cell 
                                    key={`cell-${category.idx}`}
                                    fill={colors[category.idx % colors.length]}
                                    stroke={activeIndex === index ? '#000' : 'none'}
                                    strokeWidth={2}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default InteractiveBarChart;