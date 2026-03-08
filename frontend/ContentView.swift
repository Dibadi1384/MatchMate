//
//  ContentView.swift
//  MatchMate
//
//  Created by Jason Chen on 2026-03-07.
//

/*
 
TODO:
 Load-in Page
 Login Page
 Home Page
 Profile
 Matching Query/Questionaire (with optionalities)
 Chats list
 DataUpload (temporary for development)
 Loading Screen
 Match Results/Suggestions
 Chat with match
 Post match review/questionaire

 
 */

import SwiftUI

struct ContentView: View {
    var body: some View {
        
        ZStack {
            Color("AppCream")
                .ignoresSafeArea()
            
            VStack {
                

                Image("Icon")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 250, height: 250)
                    .foregroundStyle(.tint)
                
                //offset(y: -50)
                //.padding(.top, -100)
                Text("MatchMate")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .offset(y: -50)
                
                Text("Behavior-Based Social Matching")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .offset(y: -50)
                
                
                
            }
            .padding()
        }
    }
}

#Preview {
    ContentView()
}
