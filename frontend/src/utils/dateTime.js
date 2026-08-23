/**
 * PRODEXA Unified Date/Time Utility
 * Ensures all UTC timestamps are accurately converted and formatted in the user's local browser timezone.
 */

export const getDeviceTimeZone = () => {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch {
    return 'UTC';
  }
};

export const getTimeZoneAbbr = (date = new Date()) => {
  try {
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZoneName: 'short'
    });
    const parts = formatter.formatToParts(date);
    const tz = parts.find((p) => p.type === 'timeZoneName');
    return tz ? tz.value : '';
  } catch {
    return '';
  }
};

export const parseSafeDate = (isoStr) => {
  if (!isoStr || typeof isoStr !== 'string' && !(isoStr instanceof Date)) {
    return null;
  }
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return null;
    return d;
  } catch {
    return null;
  }
};

/**
 * Formats a timestamp to full exact local date & time with timezone abbreviation.
 * Example: "23 Aug 2026, 06:12 PM IST"
 */
export const formatDateTime = (isoStr) => {
  const d = parseSafeDate(isoStr);
  if (!d) return 'Date unavailable';

  try {
    const datePart = d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
    const timePart = d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    const tzPart = getTimeZoneAbbr(d);

    return `${datePart}, ${timePart}${tzPart ? ' ' + tzPart : ''}`;
  } catch {
    return d.toLocaleString();
  }
};

/**
 * Formats a timestamp to local date only.
 * Example: "23 Aug 2026"
 */
export const formatDate = (isoStr) => {
  const d = parseSafeDate(isoStr);
  if (!d) return 'Date unavailable';

  try {
    return d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return d.toDateString();
  }
};

/**
 * Formats a timestamp to local time only with timezone.
 * Example: "06:12 PM IST"
 */
export const formatTime = (isoStr) => {
  const d = parseSafeDate(isoStr);
  if (!d) return 'Time unavailable';

  try {
    const timePart = d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    const tzPart = getTimeZoneAbbr(d);
    return `${timePart}${tzPart ? ' ' + tzPart : ''}`;
  } catch {
    return d.toTimeString();
  }
};

/**
 * Calculates calendar-based relative time in the user's local timezone.
 * - Today: same calendar day
 * - Yesterday: 1 calendar day before
 * - 2..6 days ago: N calendar days before
 * - 7+ days ago or past years: formatted date e.g. "15 Aug 2026"
 */
export const formatRelativeTime = (isoStr) => {
  const targetDate = parseSafeDate(isoStr);
  if (!targetDate) return 'Recently';

  const now = new Date();

  // Local calendar midnight comparison
  const nowMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const targetMidnight = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate());

  const diffMs = nowMidnight.getTime() - targetMidnight.getTime();
  const diffDays = Math.round(diffMs / (24 * 60 * 60 * 1000));

  if (diffDays === 0) {
    return 'Today';
  }
  if (diffDays === 1) {
    return 'Yesterday';
  }
  if (diffDays > 1 && diffDays < 7) {
    return `${diffDays} days ago`;
  }
  if (diffDays < 0) {
    return 'Upcoming';
  }
  return formatDate(isoStr);
};

export default {
  getDeviceTimeZone,
  getTimeZoneAbbr,
  parseSafeDate,
  formatDateTime,
  formatDate,
  formatTime,
  formatRelativeTime
};
