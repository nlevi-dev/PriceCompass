import { useState, useMemo } from 'react';
import { PieChart, Pie, Sector, Cell, ResponsiveContainer } from 'recharts';

export function generateColors(count) {
  const GOLDEN_ANGLE = 137.508;
  return Array.from({ length: count }, (_, i) => {
    const hue = (i * GOLDEN_ANGLE) % 360;
    const lightness = [40, 60][i % 2]; 
    return `hsl(${Math.floor(hue)}, 100%, ${lightness}%)`;
  });
}

const InteractivePieChart = ({ data, colors, onPieEnter = (_) => _, onPieLeave = (_) => _, onPieClick = (_) => _ }) => {

    const dataFiltered = useMemo(() => data.filter(d => d.sum > 0), [data]);

    const [activeIndex, setActiveIndex] = useState(null);

    if (dataFiltered.length === 0) {
        return <div style={{ width: '100%', height: '200px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <p style={{ fontSize: '18px', color: '#666' }}>no data to display</p>
        </div>;
    }

    const renderActiveShape = (props) => {
        const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill } = props;
        return (
            <g>
                <Sector
                    cx={cx}
                    cy={cy}
                    innerRadius={innerRadius}
                    outerRadius={outerRadius}
                    startAngle={startAngle}
                    endAngle={endAngle}
                    fill={fill}
                    stroke="#000"
                    strokeWidth={2}
                    strokeLinejoin="round"
                    cursor="pointer"
                />
            </g>
        );
    };

    const renderLabel = ({ cx, cy, midAngle, outerRadius, percent }) => {
        const RADIAN = Math.PI / 180;
        const radius = outerRadius + 25;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);
        const isRightSide = x > cx;
        return (
            <text
                x={x}
                y={y}
                fill="black"
                textAnchor={isRightSide ? "start" : "end"}
                dominantBaseline="central"
            >
                {(percent * 100).toFixed(0)}%
            </text>
        );
    };

    const onPieEnter_ = (data, index) => {
        onPieEnter(data.name);
        setActiveIndex(index);
    };

    const onPieLeave_ = (data) => {
        onPieLeave(data.name);
        setActiveIndex(null);
    };

    const onChartLeave_ = () => {
        onPieLeave(null);
        setActiveIndex(null);
    };

    const onPieClick_ = (data) => {
        onPieClick(data.name);
    };

    return (
        <div className="flex justify-center w-full">
            <div style={{width: '300px', height: '250px'}} onMouseLeave={onChartLeave_}>
                <ResponsiveContainer>
                    <PieChart>
                        <Pie
                            activeIndex={activeIndex}
                            activeShape={renderActiveShape}
                            data={dataFiltered}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={80}
                            paddingAngle={2}
                            stroke="none"
                            dataKey="sum"
                            isAnimationActive={false}
                            onMouseEnter={onPieEnter_}
                            onMouseLeave={onPieLeave_}
                            onClick={onPieClick_}
                            label={renderLabel}
                            cursor="pointer"
                        >
                            {dataFiltered.map(category => (
                                <Cell stroke="none" key={`cell-${category.idx}`} fill={colors[category.idx % colors.length]} />
                            ))}
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
export default InteractivePieChart;


