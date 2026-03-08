//
//  MatchMateApp.swift
//  MatchMate
//
//  Created by Jason Chen on 2026-03-07.
//

import SwiftUI

@main
struct MatchMateApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
