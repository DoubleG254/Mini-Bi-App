/* @refresh reload */
import './index.css';
import { render } from 'solid-js/web';

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

// wrapper components so the guard runs inside a Route context
const PublicRegister = () => (
  <PublicRoute>
    <Register />
  </PublicRoute>
);

const PublicSignIn = () => (
  <PublicRoute>
    <SignInPage />
  </PublicRoute>
);

const ProtectedDashboard = () => (
  <ProtectedRoute>
    <DashboardPage />
  </ProtectedRoute>
);

const ProtectedAnalytics = () => (
  <ProtectedRoute>
    <AnalyticsPage />
  </ProtectedRoute>
);

const ProtectedUpload = () => (
  <ProtectedRoute>
    <UploadPage />
  </ProtectedRoute>
);

const ProtectedHistory = () => (
  <ProtectedRoute>
    <HistoryPage />
  </ProtectedRoute>
);

render(
  () => (
    <Router>
      <Route path="/" component={PublicSignIn} />
      <Route path="/register" component={PublicRegister} />

      <Route path="/dashboard" component={ProtectedDashboard} />
      <Route path="/analytics/:datasetId" component={ProtectedAnalytics} />
      <Route path="/upload" component={ProtectedUpload} />
      <Route path="/history" component={ProtectedHistory} />
    </Router>
  ),
  root,
);
