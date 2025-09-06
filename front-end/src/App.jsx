// App.jsx (React front end for AI Personal Trainer)
import React, { useState } from 'react';
import axios from 'axios';
import "./App.css";

function App() {

  //set usestates for function call App(). these are run every update unless using a function call
  const [goal, setGoal] = useState('lose');
  const [duration, setDuration] = useState(60);
  const [workDay, setWorkDay] = useState('push');
  const [painArea, setPainArea] = useState('');
  const [painPreference, setPainPreference] = useState('avoid');
  const [workout, setWorkout] = useState(null);
  const [error, setError] = useState('');

  const generateWorkout = async () => {
    //reset workout
    setError('');
    setWorkout(null);
    //axios to handle post to backend
    try {
      const response = await axios.post('http://localhost:5001/workout', {
        goal,
        duration: parseInt(duration),
        work_day: workDay,
        pain_area: painArea,
        pain_preference: painPreference
      });
      //change state for workout to data
      setWorkout(response.data);
    } catch (err) {
      //change state for error with error msg
      setError(err.response?.data?.error || 'Failed to fetch workout plan.');
    }
  };

  return (//react front end
    <div style={{ maxWidth: 600, margin: 'auto', padding: 20 }}>
      {/*questionare with prefilled state values and using change state functions on change*/}
      <h1>AI Personal Trainer</h1>

      <label>Goal:</label>
      <select value={goal} onChange={e => setGoal(e.target.value)}>
        <option value="lose">Lose Weight</option>
        <option value="gain">Gain Weight</option>
      </select>

      <br /><br />
      <label>Duration (minutes):</label>
      <input
        type="number"
        value={duration}
        onChange={e => setDuration(e.target.value)}
        min={20}
      />

      <br /><br />
      <label>Workout Focus:</label>
      <select value={workDay} onChange={e => setWorkDay(e.target.value)}>
        <option value="push">Push</option>
        <option value="pull">Pull</option>
        <option value="leg">Leg</option>
      </select>

      <br /><br />
      <label>Injury/Pain Area (optional):</label>
      <input
        type="text"
        value={painArea}
        onChange={e => setPainArea(e.target.value)}
        placeholder="e.g. knee, shoulder"
      />

      <br /><br />
      <label>Preference:</label>
      <select value={painPreference} onChange={e => setPainPreference(e.target.value)}>
        <option value="avoid">Avoid Using</option>
        <option value="address">Address / Strengthen</option>
      </select>

      {/*On click generate button send call to backend using generateWorkout() function to call chat api*/}
      <br /><br />
      <button onClick={generateWorkout}>Generate Workout</button>

      {/*If error exists display it in red*/}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/*Display workout if it exists. loop through map and use li to list items. */}
      {workout && (
        <div>
          <h2>Workout Plan</h2>
          <p><strong>Warmup:</strong> {workout.warmup?.description || workout.warmup}</p>
          <ul>
            {workout.exercises.map((ex, idx) => (
              <li key={idx}>
                <strong>{ex.name}</strong> - {ex.description}<br />
                {ex.sets && ex.reps && <span>Sets: {ex.sets}, Reps: {ex.reps}</span>}<br />
                {ex.duration && <span>Duration: {ex.duration}</span>}<br />
                <em>Type: {ex.type}</em>
              </li>
            ))}
          </ul>
          <p><strong>Cooldown:</strong> {workout.cooldown?.description || workout.cooldown}</p>
        </div>
      )}
    </div>
  );
}

export default App;
