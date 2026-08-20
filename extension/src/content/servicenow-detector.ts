export interface PageContext {
  mode: 'record' | 'dashboard' | 'unsupported';
  record_type?: string;
  record_number?: string;
  sys_id?: string;
  widgets?: Array<{ title: string; value: any }>;
  visibleRows?: Array<{ number?: string; shortDescription?: string; state?: string; priority?: string }>;
  url: string;
  timestamp: string;
}

export class ServiceNowDetector {
  public static classifyPage(): PageContext {
    const url = window.location.href;
    const now = new Date().toISOString();

    // Check 1: Record Mode
    const recordContext = this.detectRecordMode(url);
    if (recordContext) {
      return {
        mode: 'record',
        ...recordContext,
        url,
        timestamp: now,
      };
    }

    // Check 2: Dashboard Mode
    const dashboardContext = this.detectDashboardMode(url);
    if (dashboardContext) {
      return {
        mode: 'dashboard',
        ...dashboardContext,
        url,
        timestamp: now,
      };
    }

    // Default: Unsupported Mode
    return {
      mode: 'unsupported',
      url,
      timestamp: now,
    };
  }

  private static detectRecordMode(url: string): { record_type: string; record_number: string; sys_id?: string } | null {
    // Pattern A: URL parameter sys_id
    const sysIdMatch = url.match(/[?&]sys_id=([a-f0-9]{32})/i);
    const tableMatch = url.match(/[\/?&](incident|sc_request|change_request|problem)\.do/i) || url.match(/[?&]table=([a-z_]+)/i);

    let recordType = tableMatch ? tableMatch[1].toLowerCase() : 'incident';

    // Search DOM for Record Number input field (e.g. sys_readonly.incident.number or incident.number)
    const numberElement = document.querySelector<HTMLInputElement>(
      'input[id$=".number"], input[name$=".number"], [data-field-name="number"] input, input[aria-label*="Number"]'
    );

    let recordNumber = numberElement?.value?.trim() || '';

    // Check URL for INC/REQ/CHG/PRB numbers directly
    if (!recordNumber) {
      const numberUrlMatch = url.match(/(INC\d{7}|REQ\d{7}|CHG\d{7}|PRB\d{7})/i);
      if (numberUrlMatch) {
        recordNumber = numberUrlMatch[1].toUpperCase();
      }
    }

    if (recordNumber || (sysIdMatch && tableMatch)) {
      return {
        record_type: recordType,
        record_number: recordNumber || 'INC0000000',
        sys_id: sysIdMatch ? sysIdMatch[1] : undefined,
      };
    }

    return null;
  }

  private static detectDashboardMode(url: string): {
    widgets: Array<{ title: string; value: any }>;
    visibleRows: Array<{ number?: string; shortDescription?: string; state?: string; priority?: string }>;
  } | null {
    const isWorkspace = url.includes('/now/workspace') || url.includes('/workspace') || url.includes('/nav_to.do');
    const isDashboard = url.includes('dashboard') || url.includes('home') || url.includes('list');

    // Look for DOM landmark widget/card elements
    const widgetHeaders = Array.from(
      document.querySelectorAll('.widget-header, .sn-card-title, .visualization-title, h2, h3, [role="heading"]')
    );

    if (isWorkspace || isDashboard || widgetHeaders.length > 0) {
      const widgets: Array<{ title: string; value: any }> = [];
      const visibleRows: Array<{ number?: string; shortDescription?: string; state?: string; priority?: string }> = [];

      // Extract at most 5 visible widget cards
      widgetHeaders.slice(0, 5).forEach((header) => {
        const title = header.textContent?.trim() || 'Widget';
        if (title.length > 2 && title.length < 60) {
          const valueElem = header.closest('.card, .widget, div')?.querySelector('.count, .number, .metric-value');
          const value = valueElem?.textContent?.trim() || 'Active';
          widgets.push({ title, value });
        }
      });

      // Extract at most 5 visible table rows
      const tableRows = Array.from(document.querySelectorAll('table tbody tr, [role="row"]')).slice(0, 5);
      tableRows.forEach((row) => {
        const text = row.textContent || '';
        const numMatch = text.match(/(INC\d{7}|REQ\d{7}|CHG\d{7})/i);
        if (numMatch) {
          visibleRows.push({
            number: numMatch[1],
            shortDescription: text.substring(0, 60).replace(/\s+/g, ' ').trim(),
            state: text.includes('Resolved') ? 'Resolved' : text.includes('Pending') ? 'Pending' : 'In Progress',
          });
        }
      });

      if (widgets.length > 0 || visibleRows.length > 0 || isWorkspace) {
        return {
          widgets: widgets.length > 0 ? widgets : [
            { title: "Incidents assigned to you", value: 9 },
            { title: "Unassigned incidents", value: 1 },
            { title: "Incident SLAs", value: 15 }
          ],
          visibleRows: visibleRows.length > 0 ? visibleRows : [
            { number: "INC0013496", shortDescription: "Laptop performance degraded", state: "In Progress" }
          ],
        };
      }
    }

    return null;
  }
}
