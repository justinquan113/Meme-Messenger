import { useState } from 'react'

import './App.css'

function App() {
  
  const [isPhoneNumber, setIsPhoneNumber] = useState('')
 
  function handleSubmit(){

  }

  return (
    <div class='flex justify-center items-center h-screen bg-green-400' >
      <form class='flex justify-center w-1/3 h-1/4 bg-gray-100 rounded-md'>
        <div class='flex flex-col gap-5'>
          <h1 class='font-bold lg:text-3xl text-2xl text-center'>Sign up for Daily Memes</h1>
          <div class='flex flex-col gap-2'>
            <label>Phone Number</label>
            <input 
              onChange={e => setIsPhoneNumber(e.target.value)} 
              placeholder='Enter Phone Number'
              type='text'
              required
              
            />
          </div>
          <button class='w-3/4 bg-blue-300 rounded-md self-center cursor-pointer' onSubmit={handleSubmit}>Enter</button>
        </div>
      </form>
    </div>
  )
}

export default App
