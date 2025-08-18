import React from 'react'

export default function FormContainer({title, border, children}) {
    return (
        <div className={`${border==='none'?'': 'border border-hexblue'}`}>
            <h2 className='p-4 bg-hexblue text-white text-2xl font-bold text-center'>{title}</h2>
            <div className='flex flex-wrap gap-2 p-4'>{children}</div>
        </div>
    )
}
