import React from 'react';
import { Calendar } from 'lucide-react';

const Schedule: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Schedule</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your scheduled posts and publishing timeline
        </p>
      </div>
      
      <div className="card">
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium">Post Scheduling</p>
            <p className="text-sm">This feature will be implemented soon</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Schedule;
