import React from 'react';
import Sidebar from '@/components/Sidebar';

/**
 * LayoutShell: Shared shell to keep a consistent gray theme and sidebar across pages.
 * Props:
 *  - children: page content
 *  - sidebarProps: props forwarded to Sidebar (user, conversations, handlers)
 *  - header: optional header node rendered above content
 */
export default function LayoutShell({ children, sidebarProps = {}, header = null, showSidebar = true }) {
  return (
    <div className="min-h-screen bg-[#f5f6f8] text-slate-900">
      {showSidebar && <Sidebar {...sidebarProps} />}
      <div className={`flex flex-col ${showSidebar ? 'md:ml-64' : ''} min-h-screen`}>
        {header}
        <div className="flex-1 flex flex-col">
          <div className="flex-1">{children}</div>
        </div>
      </div>
    </div>
  );
}
