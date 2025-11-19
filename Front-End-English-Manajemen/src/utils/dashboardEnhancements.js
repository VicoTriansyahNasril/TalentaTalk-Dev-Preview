// src/utils/dashboardEnhancements.js

const DashboardEnhancements = {
  defaultSettings: {
    activityLimit: 10,
    daysBack: 30,
    customLimit: false,
    customLimitValue: 10
  },

  // Configuration options
  limitOptions: {
    predefinedLimits: [
      { value: 10, label: "10 Activities", description: "Quick Overview" },
      { value: 25, label: "25 Activities", description: "Moderate Detail" },
      { value: 50, label: "50 Activities", description: "Detailed View" },
      { value: 100, label: "100 Activities", description: "Comprehensive View" },
    ],
    customLimit: {
      min: 1,
      max: 200,
      step: 1,
      label: "Custom Amount",
      description: "Choose specific number (1-200)"
    },
    daysBackOptions: [
      { value: 7, label: "Last 7 Days" },
      { value: 14, label: "Last 2 Weeks" },
      { value: 30, label: "Last 30 Days" },
      { value: 60, label: "Last 2 Months" },
      { value: 90, label: "Last 3 Months" },
    ]
  },

  // Activity type configurations
  activityTypeConfigs: {
    'Word Practice': {
      icon: 'BookIcon',
      color: 'primary',
      category: 'pronunciation'
    },
    'Sentence Practice': {
      icon: 'BookIcon', 
      color: 'info',
      category: 'pronunciation'
    },
    'Phoneme Exam': {
      icon: 'QuizIcon',
      color: 'secondary', 
      category: 'pronunciation'
    },
    'Conversation': {
      icon: 'ChatIcon',
      color: 'success',
      category: 'speaking'
    },
    'Interview': {
      icon: 'MicIcon',
      color: 'warning',
      category: 'speaking'
    }
  },

  // Validation functions
  validateActivityLimit: (limit) => {
    const numLimit = parseInt(limit);
    if (isNaN(numLimit) || numLimit < 1) return 1;
    if (numLimit > 200) return 200;
    return numLimit;
  },

  validateDaysBack: (daysBack) => {
    const numDaysBack = parseInt(daysBack);
    if (isNaN(numDaysBack) || numDaysBack < 1) return 1;
    if (numDaysBack > 90) return 90;
    return numDaysBack;
  },

  // UI Helper functions
  renderQuickLimitButtons: (currentLimit, isCustom, onLimitChange) => {
    return DashboardEnhancements.limitOptions.predefinedLimits.map(option => ({
      key: option.value,
      variant: (currentLimit === option.value && !isCustom) ? "contained" : "outlined",
      size: "small",
      onClick: () => onLimitChange(option.value),
      text: option.value.toString(),
      sx: { minWidth: 'auto', px: 1.5 }
    }));
  },

  generateInfoMessage: (settings, totalActivities, dateRange) => {
    const currentLimit = settings.customLimit ? settings.customLimitValue : settings.activityLimit;
    let message = `Showing ${currentLimit} activities per category from the ${dateRange.toLowerCase()}`;
    
    if (settings.customLimit) {
      message += " (Custom limit)";
    }
    
    return message;
  },

  generateActivityBadges: (pronunciationCount, speakingCount, totalCount) => {
    return {
      pronunciation: {
        count: pronunciationCount,
        color: "primary",
        title: `${pronunciationCount} pronunciation activities`
      },
      speaking: {
        count: speakingCount,
        color: "success", 
        title: `${speakingCount} speaking activities`
      },
      total: {
        count: totalCount,
        color: "info",
        title: `${totalCount} total activities`
      }
    };
  },

  generateEmptyStateMessage: (dateRange, currentLimit) => {
    let message = `No learning activities found in the ${dateRange.toLowerCase()}.`;
    
    if (currentLimit !== 10) {
      message += ` Try adjusting the time range or activity limit (currently ${currentLimit}).`;
    } else {
      message += " Try adjusting the time range or encourage talents to start their practice!";
    }
    
    return message;
  },

  getWPMColorAndMessage: (wpm) => {
    if (!wpm) return { color: 'default', message: 'No data' };
    
    const value = parseFloat(String(wpm).replace(/[^0-9.]/g, '') || 0);
    
    if (value >= 150) {
      return { color: 'success', message: 'Excellent fluency' };
    } else if (value >= 100) {
      return { color: 'warning', message: 'Good fluency' };
    } else if (value >= 50) {
      return { color: 'info', message: 'Moderate fluency' };
    } else {
      return { color: 'default', message: 'Needs improvement' };
    }
  },

  getScoreColorAndMessage: (score) => {
    if (!score) return { color: 'default', message: 'No score' };
    
    const value = parseFloat(String(score).replace('%', '') || 0);
    
    if (value >= 90) {
      return { color: 'success', message: 'Excellent' };
    } else if (value >= 80) {
      return { color: 'success', message: 'Good' };
    } else if (value >= 70) {
      return { color: 'warning', message: 'Fair' };
    } else if (value >= 60) {
      return { color: 'warning', message: 'Needs improvement' };
    } else {
      return { color: 'error', message: 'Poor' };
    }
  },

  generateActivitySummary: (pronunciationActivities, speakingActivities, settings) => {
    const currentLimit = settings.customLimit ? settings.customLimitValue : settings.activityLimit;
    
    return {
      pronunciation: {
        count: pronunciationActivities.length,
        limit: currentLimit,
        hasMore: pronunciationActivities.length === currentLimit,
        types: pronunciationActivities.reduce((acc, activity) => {
          acc[activity.activityType] = (acc[activity.activityType] || 0) + 1;
          return acc;
        }, {})
      },
      speaking: {
        count: speakingActivities.length,
        limit: currentLimit,
        hasMore: speakingActivities.length === currentLimit,
        types: speakingActivities.reduce((acc, activity) => {
          acc[activity.activityType] = (acc[activity.activityType] || 0) + 1;
          return acc;
        }, {})
      },
      dateRange: `Last ${settings.daysBack} days`,
      totalFound: pronunciationActivities.length + speakingActivities.length
    };
  },

  generateTableFooterInfo: (activities, limit, type) => {
    const count = activities.length;
    const hasMore = count === limit;
    
    let message = `Showing ${count} ${type} activities`;
    
    if (hasMore) {
      message += ` (limit reached - there may be more)`;
    }
    
    if (count > 0) {
      const latestDate = activities[0]?.lastActivity;
      const oldestDate = activities[activities.length - 1]?.lastActivity;
      
      if (latestDate && oldestDate) {
        message += ` • From ${new Date(oldestDate).toLocaleDateString()} to ${new Date(latestDate).toLocaleDateString()}`;
      }
    }
    
    return message;
  },

  saveSettings: (settings) => {
    try {
      localStorage.setItem('dashboardSettings', JSON.stringify(settings));
      return true;
    } catch (error) {
      console.error('Failed to save dashboard settings:', error);
      return false;
    }
  },

  loadSettings: () => {
    try {
      const saved = localStorage.getItem('dashboardSettings');
      return saved ? JSON.parse(saved) : DashboardEnhancements.defaultSettings;
    } catch (error) {
      console.error('Failed to load dashboard settings:', error);
      return DashboardEnhancements.defaultSettings;
    }
  },

  trackSettingsChange: (oldSettings, newSettings) => {
    const changes = {};
    
    if (oldSettings.activityLimit !== newSettings.activityLimit) {
      changes.activityLimit = {
        from: oldSettings.activityLimit,
        to: newSettings.activityLimit
      };
    }
    
    if (oldSettings.daysBack !== newSettings.daysBack) {
      changes.daysBack = {
        from: oldSettings.daysBack,
        to: newSettings.daysBack
      };
    }
    
    if (oldSettings.customLimit !== newSettings.customLimit) {
      changes.customLimit = {
        from: oldSettings.customLimit,
        to: newSettings.customLimit
      };
    }
    
    if (Object.keys(changes).length > 0) {
      console.log('Dashboard settings changed:', changes);
    }
  },

  settingsDialogConfig: {
    title: "Dashboard Activity Settings",
    sections: [
      {
        title: "Activities per Category",
        description: "Choose how many activities to display for each category (pronunciation and speaking)",
        type: "activityLimit"
      },
      {
        title: "Time Range", 
        description: "Select how far back to look for recent activities",
        type: "daysBack"
      }
    ]
  }
};

export default DashboardEnhancements;