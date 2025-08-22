import * as React from 'react';
import { useAccountContext } from 'frontend/contexts';
import { DashboardPage } from 'frontend/components/dashboard';

const Dashboard: React.FC = () => {
  const { accountDetails, isAccountLoading } = useAccountContext();

  if (isAccountLoading || !accountDetails) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading account information...</p>
      </div>
    );
  }

  return <DashboardPage accountId={accountDetails.id} />;
};

export default Dashboard;
