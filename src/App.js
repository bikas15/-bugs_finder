import React from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import Home from './components/Home';
import Bugs from './components/Bugs';
import About from './components/About';
import Contact from './components/Contact';
import CustomerStories from './components/CustomerStories';
import Navbar from './components/Navbar';
import Footer from './components/Footer'; 
import './App.css';
import './styles.css'; 

function App() {
  return (
    <div className="App">
      <Router>
        <Navbar />
        <Route path="/" exact component={Home} />
        <Route path="/bugs" component={Bugs} />
        <Route path="/about" component={About} />
        <Route path="/contact" component={Contact} />
        <Route path="/customer-stories" component={CustomerStories} />
        <Footer /> {/* Add Footer component */} </Router>
    </div>
  );
}

export default App;
