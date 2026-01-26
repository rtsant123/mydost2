import React from 'react';
import Sidebar from '@/components/Sidebar';

/**
 * LayoutShell: Shared shell to keep a consistent gray theme and sidebar across pages.
 * Props:
 *  - children: page content
 *  - sidebarProps: props forwarded to Sidebar (user, conversations, handlers)
 *  - header: optional header node rendered above content
 */
export default function LayoutShell({ children, sidebarProps = {}, header = null }) {
  return (
    <div className="min-h-screen bg-[#f5f6f8] text-slate-900">
      <Sidebar {...sidebarProps} />
      <div className="flex flex-col md:ml-64 min-h-screen overflow-hidden">
        {header}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">{children}</div>
        </div>
      </div>
    </div>
  );
}
