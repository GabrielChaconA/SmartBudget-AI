import * as echarts from 'echarts/core'

export const CHART_COLORS = {
  background: 'transparent',
  primary: '#1DA1F2', // Bright blue
  positive: '#22C55E',
  negative: '#EF4444',
  textPrimary: '#FFFFFF',
  textSecondary: '#A1A1AA',
  textTertiary: '#6B7280',
  gridLine: 'rgba(255,255,255,0.08)',
  tooltipBg: '#18181b', // Dark background for tooltip
  tooltipBorder: 'rgba(255,255,255,0.05)',
  pieColors: ['#4ade80', '#22c55e', '#16a34a', '#15803d', '#166534', '#14532d'],
  distinctColors: [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ec4899', // pink
    '#8b5cf6', // purple
    '#06b6d4', // cyan
    '#ef4444', // red
    '#84cc16', // lime
    '#f97316', // orange
    '#14b8a6', // teal
  ]
}

export const getTranslucentStyle = (hex: string, opacity = 0.2) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return {
    color: `rgba(${r}, ${g}, ${b}, ${opacity})`,
    borderColor: hex,
    borderWidth: 2
  }
}

export const commonTooltip = {
  backgroundColor: CHART_COLORS.tooltipBg,
  borderColor: CHART_COLORS.tooltipBorder,
  borderRadius: 8,
  padding: [8, 12],
  textStyle: {
    color: CHART_COLORS.textSecondary,
    fontSize: 12
  },
  transitionDuration: 0.3
}

export const commonGrid = {
  top: 40,
  right: 20,
  bottom: 30,
  left: 20,
  containLabel: true
}

export const commonXAxis = {
  axisLine: { show: false },
  axisTick: { show: false },
  axisLabel: { 
    color: CHART_COLORS.textSecondary, 
    margin: 16,
    fontFamily: 'Inter, Geist, sans-serif'
  },
  splitLine: { show: false }
}

export const commonYAxis = {
  axisLine: { show: false },
  axisTick: { show: false },
  axisLabel: { 
    color: CHART_COLORS.textTertiary,
    fontFamily: 'Inter, Geist, sans-serif'
  },
  splitLine: { 
    show: true, 
    lineStyle: { 
      type: 'dashed', 
      color: CHART_COLORS.gridLine 
    } 
  }
}

// For Line/Area charts
export const getAreaGradient = () => {
  return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: 'rgba(29,161,242,0.25)' },
    { offset: 1, color: 'rgba(29,161,242,0)' }
  ])
}

export const commonLineSeriesProps = {
  smooth: true,
  showSymbol: false,
  symbolSize: 6,
  itemStyle: { color: CHART_COLORS.primary },
  lineStyle: { 
    width: 3, 
    color: CHART_COLORS.primary, 
    cap: 'round' as const,
    join: 'round' as const
  },
  animationDuration: 400,
  animationEasing: 'cubicOut'
}
