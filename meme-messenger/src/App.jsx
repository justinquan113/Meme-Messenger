import { useState } from 'react'

import './App.css'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:5000'

function App() {

  const [phoneNumber, setPhoneNumber] = useState('')
  const [message, setMessage] = useState('')
  function handleSubmit(e){
    e.preventDefault()
    fetch(`${API_URL}/submit/${phoneNumber}`)
     .then(response =>{
        return response.json()
    })
    .then(data =>{
        let message = data.message

        setMessage(message)
      })
    .catch(error => {
      console.log(error)
      setMessage('Something went wrong. Please try again.')
    })

    setPhoneNumber('')

    }

  return (
  <div className="flex justify-center items-center min-h-screen bg-amber-50 p-4">

    <form
      onSubmit={handleSubmit}
      className="w-full max-w-md bg-white shadow-2xl rounded-2xl p-8 flex flex-col gap-6 transition-all duration-300 hover:scale-[1.02]"
    >
      
      <h1 className="text-3xl font-extrabold text-center text-gray-800">
         Meme Messenger
      </h1>
      <p className="text-center text-gray-500 text-sm">
        Get fresh memes sent straight to your phone every day.
      </p>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-gray-700">
          Phone Number
        </label>

        <input
          onChange={(e) => setPhoneNumber(e.target.value)}
          placeholder="e.g. 14035551234"
          type="tel"
          required
          value={phoneNumber}
          pattern="^1[2-9][0-9]{9}$"
          onInvalid={(e) =>
            e.target.setCustomValidity(
              "Enter a valid 10-digit phone number starting with a valid area code"
            )
          }
          onInput={(e) => e.target.setCustomValidity("")}
          className="px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all duration-200 shadow-sm"
        />
      </div>

      <button
        type="submit"
        className="bg-violet-600 hover:bg-violet-700 text-white font-semibold py-3 rounded-lg shadow-md hover:shadow-xl hover:scale-105 active:scale-95 transition-all duration-200"
      >
         Send Me Memes
      </button>

      {message && (
        <p className="text-center text-sm text-green-600 font-medium">
          {message}
        </p>
      )}
    </form>
  </div>
);
}

export default App
