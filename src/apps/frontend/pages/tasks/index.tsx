import * as React from 'react';
import { useAccountContext } from 'frontend/contexts';
import { TasksPage } from 'frontend/components/tasks';

const Tasks: React.FC = () => {
  const { accountDetails, isAccountLoading } = useAccountContext();

  if (isAccountLoading || !accountDetails) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading account information...</p>
      </div>
    );
  }

  return <TasksPage accountId={accountDetails.id} />;
};

export default Tasks;
