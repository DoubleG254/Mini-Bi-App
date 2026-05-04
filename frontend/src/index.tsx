/* @refresh reload */
import './index.css';
import { render } from 'solid-js/web';
import 'solid-devtools';

import { Router, Route } from '@solidjs/router';
import { ProtectedRoute, PublicRoute } from './components/guards';
import Register from './components/pages/Register'
import SignInPage from './components/pages/SignIn'
import AnalyticsPage from './components/pages/Analytics'
import UploadPage from './components/pages/Upload'
import HistoryPage from './components/pages/History'
import DashboardPage from './components/pages/Dashboard'

const root = document.getElementById('root');

if (!(root instanceof HTMLElement)) {
  throw new Error(
    'Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?',
  );
}

render(() => <Router>
  <PublicRoute>
    <Route path="/register" component={Register} />
    <Route path="/" component={SignInPage} />
  </PublicRoute>

  <ProtectedRoute>
    <Route path="/dashboard" component={DashboardPage} />
    <Route path="/analytics/:datasetId" component={AnalyticsPage} />
    <Route path="/upload" component={UploadPage} />
    <Route path="/history" component={HistoryPage} />
  </ProtectedRoute>
</Router>, root);
