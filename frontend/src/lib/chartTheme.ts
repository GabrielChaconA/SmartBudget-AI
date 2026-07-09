import * as echarts from 'echarts/core'
import { useDark } from '@vueuse/core'
import { computed } from 'vue'

export const useChartTheme = () => {
  const isDark = useDark()

  return {
    get CHART_COLORS() {
      const isDarkValue = isDark.value
      return {
        background: 'transparent',
        primary: '#1DA1F2', // Bright blue
        positive: '#22C55E',
        negative: '#EF4444',
        textPrimary: isDarkValue ? '#FFFFFF' : '#0A0A0A',
        textSecondary: isDarkValue ? '#A1A1AA' : '#71717A',
        textTertiary: isDarkValue ? '#6B7280' : '#A1A1AA',
        gridLine: isDarkValue ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
        tooltipBg: isDarkValue ? '#18181b' : '#FFFFFF',
        tooltipBorder: isDarkValue ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
        pieColors: ['#4ade80', '#22c55e', '#16a34a', '#15803d', '#166534', '#14532d'],
        distinctColors: [
          '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6',
          '#06b6d4', '#ef4444', '#84cc16', '#f97316', '#14b8a6',
        ]
      }
    },

    getTranslucentStyle(hex: string, opacity = 0.2) {
      const r = parseInt(hex.slice(1, 3), 16)
      const g = parseInt(hex.slice(3, 5), 16)
      const b = parseInt(hex.slice(5, 7), 16)
      return {
        color: `rgba(${r}, ${g}, ${b}, ${opacity})`,
        borderColor: hex,
        borderWidth: 2
      }
    },

    get commonTooltip() {
      return {
        backgroundColor: this.CHART_COLORS.tooltipBg,
        borderColor: this.CHART_COLORS.tooltipBorder,
        borderRadius: 8,
        padding: [8, 12],
        textStyle: {
          color: this.CHART_COLORS.textSecondary,
          fontSize: 12
        },
        transitionDuration: 0.3
      }
    },

    get commonGrid() {
      return {
        top: 40,
        right: 20,
        bottom: 30,
        left: 20,
        containLabel: true
      }
    },

    get commonXAxis() {
      return {
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { 
          color: this.CHART_COLORS.textSecondary, 
          margin: 16,
          fontFamily: 'Inter, Geist, sans-serif'
        },
        splitLine: { show: false }
      }
    },

    get commonYAxis() {
      return {
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { 
          color: this.CHART_COLORS.textTertiary,
          fontFamily: 'Inter, Geist, sans-serif'
        },
        splitLine: { 
          show: true, 
          lineStyle: { 
            type: 'dashed', 
            color: this.CHART_COLORS.gridLine 
          } 
        }
      }
    },

    getAreaGradient() {
      return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(29,161,242,0.25)' },
        { offset: 1, color: 'rgba(29,161,242,0)' }
      ])
    },

    get commonLineSeriesProps() {
      return {
        smooth: true,
        showSymbol: false,
        symbolSize: 6,
        itemStyle: { color: this.CHART_COLORS.primary },
        lineStyle: { 
          width: 3, 
          color: this.CHART_COLORS.primary, 
          cap: 'round' as const,
          join: 'round' as const
        },
        animationDuration: 400,
        animationEasing: 'cubicOut'
      }
    }
  }
}
