/* @refresh reload */
import './index.css';
import { render } from 'solid-js/web';
import 'solid-devtools';
import { lazy } from 'solid-js';

import { Router, Route } from '@solidjs/router';
const Register = lazy(() => import('./components/pages/Register'))
const SignInPage = lazy(() => import('./components/pages/SignIn'))
const AnalyticsPage = lazy(() => import('./components/pages/Analytics'))
const UploadPage = lazy(() => import('./components/pages/Upload'))
const HistoryPage = lazy(() => import('./components/pages/History'))


const root = document.getElementById('root');

if (!(root instanceof HTMLElement)) {
  throw new Error(
    'Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?',
  );
}

render(() => <Router>
  <Route path="/register" component={Register} />
  <Route path="/" component={SignInPage} />
  <Route path="/analytics/:id" component={AnalyticsPage} />
  <Route path="/upload" component={UploadPage} />
  <Route path="/history" component={HistoryPage} />
</Router>, root);
