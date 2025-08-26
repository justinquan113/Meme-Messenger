import { useState, useEffect } from 'react'

import './App.css'

function App() {
  
  const [phoneNumber, setPhoneNumber] = useState('')
  const [message, setMessage] = useState('')
  
  function handleSubmit(e){
    e.preventDefault()
    fetch(`http://127.0.0.1:5000/submit/${phoneNumber}`)
     .then(response =>{
        return response.json()
    })
    .then(data =>{
        let message = data.message
        console.log(message)
        setMessage(message)
      })
    .catch(error => {
      console.log(error)
    })

    setPhoneNumber('')
    
    }
  

  return (
    <div className='flex justify-center items-center h-screen bg-green-400' onSubmit={handleSubmit} >
      <form className='flex justify-center w-1/3 h-1/4 bg-gray-100 rounded-md'>
        <div className='flex flex-col gap-5'>
          <h1 className='font-bold lg:text-3xl text-2xl text-center'>Sign up for Daily Memes</h1>
          <div className='flex flex-col gap-2'>
            <label>Phone Number</label>
            <input 
              onChange={e => setPhoneNumber(e.target.value)} 
              placeholder='Enter Phone Number'
              type='tel'
              required
              value={phoneNumber}
              
            />
          </div>
          <button className='w-3/4 bg-blue-300 rounded-md self-center cursor-pointer' type='submit' >Enter</button>
        </div>
        <p>{message}</p>
      </form>
      
    </div>
  )
}

export default App
