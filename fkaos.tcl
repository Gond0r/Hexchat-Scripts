# add your own aliases here
######## Global Variables ########
set fkaosconf "fkaos.conf"
set fkaosgrab "1"
set fkaosanswer "0"
set fkaosbot ""
set fkaosdb "fkaos.db"
set fkaosq ""
set fkaosha ""
set fkaosnoa ""
set fkaosa ""
set fkaosdbrec ""
set fkaosdbrrec ""
set fkaosqfound 0
set fkaosnora 0
set fkaostext ""
set fkaosdbidr 0
set fkaoschan ""
set fkaosqdone 0
######## Procedures ########
proc fkaosreadfile { filopn } {
	cd [getinfo xchatdir]
	set filopnid [open $filopn r]
	set datcont [read -nonewline $filopnid]
	close $filopnid
	return $datcont
}

proc fkaosreadconf {} {
	global fkaosconf
	global fkaosgrab
	global fkaosanswer
	global fkaosbot
	global fkaoschan
	cd [getinfo xchatdir]
	if { [file exists $fkaosconf] } {
		set fkaosconfdata [fkaosreadfile $fkaosconf]
		foreach fkaosconfdataline [split $fkaosconfdata "\n"] {
			switch -nocase [lindex $fkaosconfdataline 0] {
				"answer" {
					set fkaosanswer [lindex $fkaosconfdataline end]
				}
				"grab" {
					set fkaosgrab [lindex $fkaosconfdataline end]
				}
				"botnick" {
					set fkaosbot [lindex $fkaosconfdataline end]
				}
				"chan" {
					set fkaoschan [lindex $fkaosconfdataline end]
				}
				"" {
					print "fkaos : conf file is [bold][color 5]EMPTY OR CORRUPTED[color][bold]. Using defaults... grab:$fkaosgrab answer:$fkaosanswer"
					fkaoswriteconf
				}
			}
		}
	} else {
		print "fkaos : conf file does [bold][color 5]NOT[color][bold] exist. Using defaults... grab:$fkaosgrab answer:$fkaosanswer"
		fkaoswriteconf
	}
}
proc fkaoswriteconf {} {
	global fkaosconf
	global fkaosgrab
	global fkaosanswer
	global fkaosbot
	global fkaoschan
	cd [getinfo xchatdir]
	set fkaosconfid [open $fkaosconf w]
	puts $fkaosconfid "answer $fkaosanswer"
	puts $fkaosconfid "grab $fkaosgrab"
	puts $fkaosconfid "botnick $fkaosbot"
	puts $fkaosconfid "chan $fkaoschan"
	close $fkaosconfid
}
proc fkaoscalcnora {} {
	global fkaosdbrrec
	global fkaosnoa
	global fkaosnora
	global fkaosha
	if { $fkaosha == "-" } {
		set fkaosha $fkaosnoa
	}
	set fkaosnora [expr $fkaosnoa-$fkaosha]
	return fkaosnora
}
proc fkaoshuntqff {} {
	global fkaosqfound
	global fkaosnoa
	global fkaosnora
	global fkaosq
	global fkaostext
	global fkaosdbidr
	global fkaosdb
	set fkaosqfound 0
	set fkaosnora 0
	# K1329  NFL Teams (name, not city) 10   [10 Answers]#
	# get the string index of the first character in the question #NFL Teams (name, not city) 10   #
	set fkaosqst [expr [string first "  " $fkaostext]+2]
	# get the string index of the last character in the question #NFL Teams (name, not city) 10   #
	set fkaosqen [expr [string last "\[" $fkaostext]-1]
	set fkaosq [string range $fkaostext $fkaosqst $fkaosqen]
	while {[string index $fkaosq end] == " "} {
		set fkaosq [string range $fkaosq 0 [expr [string last " " $fkaosq]-1]]
	}
	# get the string index of the first character in the number of answers #[10 Answers]
	set fkaosnoast [expr [string last "\[" $fkaostext]+1]
	# get the string index of the last character in the number of answers #[10 Answers]
	set fkaosnoaen [expr [string last " " $fkaostext [string length $fkaostext]]-1]
	set fkaosnoa [string range $fkaostext $fkaosnoast $fkaosnoaen]
	cd [getinfo xchatdir]
	set fkaosdbidr [open $fkaosdb r]; #qsn 0	haveansw 2	allansw 4	answers 6
}
proc splitsrc { } {
  uplevel "scan \$_src \"%\\\[^!\\\]!%\\\[^@\\\]@%s\" _nick _ident _host"
}
#proc stripcolor {intext} {; #this proc isn't working well it shaves up some text during the process
#  regsub -all "(\002|\003\[0-9\]*,*\[0-9\]*|\026|\037)" $intext "" outtext
#  return $outtext
#}
proc stripcolor {str} {
    return [regsub -all -- {\002|\037|\026|\003(\d{1,2})?(,\d{1,2})?} $str ""]
}
#proc stripcode1 {str} {
#    regsub -all -- {\002|\037|\026|\003(\d{1,2})?(,\d{1,2})?} $str "" str
#    return $str
#}
proc fkaoshousekeep {} {
	set fkaosgrab 0
	set fkaosanswer 0
}
######## Actual Script ########
fkaosreadconf

on XC_CHANMSG fkaos {
	global fkaosgrab
	global fkaosanswer
	global fkaosq
	global fkaosnoa
	global fkaosha
	global fkaosnora
	global fkaosa
	global fkaosbot
	global fkaosdb
	global fkaosqfound
	global fkaosdbrrec
	global fkaosdbrec
	global fkaostext
	global fkaosdbidr
	global fkaoschan
	global fkaosbot
	global fkaoschan
	set fkaoscurbot [stripcolor [lindex $_raw 1]]
	set fkaostext [stripcolor [lindex $_raw 2]]
	if { [string match -nocase $fkaosbot $fkaoscurbot] } {
		#KAOS  v0.91.0 by Marky [1587 Questions] #
		# K0752  Top 10 Cities in Idaho  [10 Answers]#
		if { [string match { K[0-9][0-9][0-9][0-9] *\[[0-9]* Answers\]} $fkaostext] } {
			set fkaosqdone 0
			if { $fkaosgrab == "1" } {
				fkaoshuntqff
				while {![eof $fkaosdbidr]} {
					set fkaosdbrrec [gets $fkaosdbidr]
					#qsn 0	haveansw 2	allansw 4	answers 6
					if { [string match -nocase [lindex $fkaosdbrrec 0] $fkaosq] && [lindex $fkaosdbrrec 4] == $fkaosnoa} {
						set fkaosqfound 1
						set fkaosha [lindex $fkaosdbrrec 2]
						set fkaosa [lindex $fkaosdbrrec 6]
						if { $fkaosha == "-"} {
							set fkaosnora 0
							print "!!$fkaosa!!"
						} else {
							fkaoscalcnora
						}
						break
					}
				}
				close $fkaosdbidr
				if { $fkaosqfound != 1 } {
					set fkaosqfound 2
					set fkaosha 0
					set fkaosa ""
					fkaoscalcnora
					print "!!new question!!"
				}
			}
			if { $fkaosanswer == "1" } {
				if { $fkaosgrab == "1" } {
					if { $fkaosqfound == "1" } {
						print "answering [llength $fkaosa] answers"
						set fkaosidx 0
						while { $fkaosidx <= [expr [llength $fkaosa]-1] } {
							/timer -refnum [expr 9000+$fkaosidx] [expr $fkaosidx*2+1] msg $fkaoschan [lindex $fkaosa $fkaosidx]
							incr fkaosidx
							if { [string length [lindex $fkaosa $fkaosidx]] > 30 } {
								cd [getinfo xchatdir]
								set tfileid [open ToFix.db a+]
								puts $tfileid "$fkaosq"
								close $tfileid
							}
						}
						if { $fkaosha != "-" } {
							fkaoscalcnora
						}
					}
				} else {
					fkaoshuntqff
					while {![eof $fkaosdbidr]} {
						set fkaosdbrrec [gets $fkaosdbidr]
						#qsn 0	haveansw 2	allansw 4	answers 6
						if { [string match -nocase [lindex $fkaosdbrrec 0] $fkaosq] && [lindex $fkaosdbrrec 4] == $fkaosnoa} {
							set fkaosqfound 1
							print "!!question found to answer!!"
							set fkaosha [lindex $fkaosdbrrec 2]
							set fkaosa [lindex $fkaosdbrrec 6]
							set fkaosidx 0
							print "answering [llength $fkaosa] answers"
							while { $fkaosidx <= [expr [llength $fkaosa]-1] } {
								#TIMER [-refnum <num>] [-repeat <num>] <seconds> <command>
								/timer -refnum [expr 9000+$fkaosidx] [expr $fkaosidx+1] msg $fkaoschan [lindex $fkaosa $fkaosidx]
								incr fkaosidx
								if { [llength [lindex $fkaosa $fkaosidx]] > 30 } {
									cd [getinfo xchatdir]
									set tfileid [open ToFix.db a+]
									puts $tfileid "$fkaosq"
									close $tfileid
								}
							}
							if { $fkaosha != "-" } {
								fkaoscalcnora
							}
							if { $fkaosha == "-"} {
								set fkaosnora 0
							} else {
								fkaoscalcnora
							}
							break
						}
					}
					close $fkaosdbidr
				}
			}
		#Limitless wins 80 coins for Superman#
		} elseif { [string match {* wins * * for *} $fkaostext] } {
			# Someone said an answer
			if { [string match -nocase [lindex $fkaostext 0] [me]] } {
				# print "that's me you moron"
			} else {
				#[string range $fkaostext [string first [lindex $fkaostext 5] $fkaostext] end]
				set fkaosta [string range $fkaostext [string first [lindex $fkaostext 5] $fkaostext] end]
				set fkaosidx 0
				set fkaosafound 0
				if { $fkaosgrab == 1 } {
					if { $fkaosqfound != 0 } {
						fkaoscalcnora
						if { $fkaosnora != 0 } {
							if { [llength $fkaosa] != 0 } {
								while { $fkaosidx <= [expr [llength $fkaosa]-1] } {
									if { [string match -nocase [lindex $fkaosa $fkaosidx] $fkaosta] } {
										set fkaosafound 1
										print "answer_found_skipping...$fkaosidx"
										break
									}
									incr fkaosidx
								}
							}
							if { $fkaosafound != 1 } {
								lappend fkaosa $fkaosta
								print "answers now: $fkaosa"
								incr fkaosha
								fkaoscalcnora
							}
						}
					}
				}
			}
		#You Missed: Donner | Blitzen#
		} elseif { [string match {You Missed: *} $fkaostext] } {
			set fkaosrawa [string range $fkaostext 12 end]
			set fkaosrawa [string map {{ | } |} $fkaosrawa]
			set fkaostas [split $fkaosrawa |]
			set fkaosidx 0
			set fkaosafound 0
			if { $fkaosgrab == 1 } {
				if { $fkaosqfound != 0 } {
					fkaoscalcnora
					if { $fkaosnora != 0 } {
						if { $fkaosnora == $fkaosnoa } {
							set fkaosa $fkaostas
							set fkaosha 0
							cd [getinfo xchatdir]
							set fkaosdbidw [open $fkaosdb a+]
							set fkaosdbrec ""
							set fkaosdbrec [lappend fkaosdbrec $fkaosq % - % $fkaosnoa % $fkaosa]
							puts $fkaosdbidw $fkaosdbrec
							close $fkaosdbidw
						} else {
							foreach fkaosta $fkaostas {
								set fkaosafound 0
								while { $fkaosidx <= [expr [llength $fkaosa]-1] } {
									if { [string match -nocase [lindex $fkaosa $fkaosidx] $fkaosta] } {
										set fkaosafound 1
										break
									}
									incr fkaosidx
								}
								if { $fkaosafound != 1 } {
									lappend fkaosa $fkaosta
									incr fkaosha
									fkaoscalcnora
									if { $fkaosnora == 0 } {
										break
									}
								}
							}
							set fkaosha 0
							cd [getinfo xchatdir]
							set fkaosdbidw [open $fkaosdb a+]
							set fkaosdbrec ""
							set fkaosdbrec [lappend fkaosdbrec $fkaosq % - % $fkaosnoa % $fkaosa]
							puts $fkaosdbidw $fkaosdbrec
							close $fkaosdbidw
						}
					} else {
						foreach fkaosta $fkaostas {
							set fkaosafound 0
							while { $fkaosidx <= [expr [llength $fkaosa]-1] } {
								if { [string match -nocase [lindex $fkaosa $fkaosidx] $fkaosta] } {
									set fkaosafound 1
									break
								}
								incr fkaosidx
							}
							if { $fkaosafound != 1 } {
								lappend fkaosa $fkaosta
							}
						}
						cd [getinfo xchatdir]
						set fkaosdbidw [open $fkaosdb a+]
						set fkaosdbrec ""
						set fkaosdbrec [lappend fkaosdbrec $fkaosq % - % $fkaosnoa % $fkaosa]
						puts $fkaosdbidw $fkaosdbrec
						close $fkaosdbidw
					}
				}
			}
			set fkaosqdone 1
		# Total Number Answered Correctly:  6 from a possible 8! #
		#KAOS  You've Guessed Them All! Well Done! #
		} elseif { [string match {KAOS  You've Guessed Them All! Well Done! } $fkaostext] } {
			if { $fkaosanswer == "1" } {
				set fkaostidx 0
				/flushq
				while { $fkaostidx <= 100} {
					/TIMER -quiet -delete [expr 9000+$fkaostidx]
					incr fkaostidx
				}
			}
		#KAOS Bummer! Nobody got a single Answer #
		} elseif { [string match {KAOS Bummer! Nobody got a single Answer } $fkaostext] } {
			#
		#KAOS stopped by [Limitless!I@3C71E4.990EE2.D28B29.26B8B4]#
		} elseif {[string match {KAOS stopped by *} $fkaostext]} {
			set fkaosq ""
			set fkaosqfound 0
			set fkaosafound 0
			set fkaosnora 0
			set fkaosqdone 1
			set fkaostidx 0
			if { $fkaosanswer == "1" } {
				/flushq
				set fkaostidx 0
				while { $fkaostidx <= 100} {
					/TIMER -quiet -delete [expr 9000+$fkaostidx]
					incr fkaostidx
				}
			}
		}
	}
}
######## Aliases ########
alias fkaosdup {
	set fkaosdupfound 0
	cd [getinfo xchatdir]
	set pre "ORIG"
	# file copy $_rest $_rest$pre
	set fkaosdbid [open $_rest r]
	set fkaosrawdata [read $fkaosdbid]
	close $fkaosdbid
	set fkaosdata [split $fkaosrawdata "\n"]
	foreach fkaosdatarec $fkaosdata {
		set fkaosdans1 [lindex $fkaosdatarec 6]
		set fkaosdans2 [lindex $fkaosdatarec 6]
		foreach fkaosdsans2 $fkaosdans2 {
			set fkaosdupfound 0
			foreach fkaosdsans1 $fkaosdans1 {
				if { [string match -nocase $fkaosdsans2 $fkaosdsans1] } {
					set fkaosdupfound 1
				}
			}
			if { $fkaosdupfound == 1 } {
				print "duplicate answer found $fkaosdsans1 $fkaosdsans2"
			}
		}
	}
}
alias fkaoshk {
	set fkaoshkrec1 ""
	set fkaoshkrec2 ""
	set fkaoshkq1 ""
	set fkaoshkq2 ""
	set fkaoshkq ""
	set fkaoshknoa1 ""
	set fkaoshknoa2 ""
	set fkaoshknoa ""
	set fkaoshka1 ""
	set fkaoshka2 ""
	set fkaoshka ""
	cd [getinfo xchatdir]
	set pre "ORIG"
	file copy $_rest $_rest$pre
	set fkaosdbid [open $_rest r]
	set fkaosrawdata [read $fkaosdbid]
	close $fkaosdbid
	set fkaosdata [split $fkaosrawdata "\n"]
	for {set fkaoshkidx1 0} {$fkaoshkidx1 <= [expr [llength $fkaosdata]-1]} {incr fkaoshkidx1} {
		#{Common Numbers} % - % 10 % {7 007 911 13 21 747 101 7-11 99 69}
		set fkaoshkrec1 [lindex $fkaosdata $fkaoshkidx1]
		set fkaoshkq1 [lindex $fkaoshkrec1 0]
		if { $fkaoshkq1 == "-" } {
			continue
		} else {
			set fkaoshknoa1 [lindex $fkaoshkrec1 4]
			set fkaoshka1 [lindex $fkaoshkrec1 6]
			for {set fkaoshkidx2 [expr $fkaoshkidx1+1]} {$fkaoshkidx2 <= [expr [llength $fkaosdata]-1]} {incr fkaoshkidx2} {
				#{Common Numbers} % - % 10 % {7 007 911 13 21 747 101 7-11 99 69}
				set fkaoshkrec2 [lindex $fkaosdata $fkaoshkidx2]
				set fkaoshkq2 [lindex $fkaoshkrec2 0]
				if { $fkaoshkq2 == "-" } {
					continue
				} else {
					set fkaoshknoa2 [lindex $fkaoshkrec2 4]
					set fkaoshka2 [lindex $fkaoshkrec2 6]
					# start comparing
					if { [string match -nocase $fkaoshkq1 $fkaoshkq2] } {
						print "*** loop A : Q $fkaoshkidx1"
						print "*** loop B : Q $fkaoshkidx2"
						print "*** loop B : found duplicate question. processing... "
						if { $fkaoshknoa1 == $fkaoshknoa2 } {
							print "*** loop B : found same no of answers. processing... "
							if { [string match -nocase $fkaoshka1 $fkaoshka2] } {
								print "*** loop B : found same answers. deleted! skipping... "
								lset fkaosdata $fkaoshkidx2 0 "-"
								continue
							} else {
								print "*** loop B : found different answers. merging... "
								print "*** loop B : Answer A: $fkaoshka1 "
								print "*** loop B : Answer B: $fkaoshka2 "
								#merge answers
								set fkaoshka $fkaoshka1
								foreach fkaoshksa2 $fkaoshka2 {
									set fkaoshkafound 0
									foreach fkaoshksa1 $fkaoshka1 {
										if { [string match -nocase $fkaoshksa2 $fkaoshksa1] } {
											set fkaoshkafound 1
										}
									}
									if { $fkaoshkafound != 1 } {
										lappend fkaoshka $fkaoshksa2
									}
								}
								# update records
								print "*** loop B : result : $fkaoshka "
								set fkaoshka1 $fkaoshka
								lset fkaosdata $fkaoshkidx1 6 $fkaoshka
								lset fkaosdata $fkaoshkidx2 0 "-"
							}
						} else {
							print "*** loop B : found different no of answers. $fkaoshknoa1/$fkaoshknoa2 merging... "
							print "*** loop B : Answer A: $fkaoshka1 "
							print "*** loop B : Answer B: $fkaoshka2 "
							#merge answers
							set fkaoshka $fkaoshka1
							foreach fkaoshksa2 $fkaoshka2 {
								set fkaoshkafound 0
								foreach fkaoshksa1 $fkaoshka1 {
									if { [string match -nocase $fkaoshksa2 $fkaoshksa1] } {
										set fkaoshkafound 1
									}
								}
								if { $fkaoshkafound != 1 } {
									lappend fkaoshka $fkaoshksa2
								}
							}
							# update records
							#{Common Numbers} % - % 10 % {7 007 911 13 21 747 101 7-11 99 69}
							print "*** loop B : result : $fkaoshka "
							set fkaoshka1 $fkaoshka
							set fkaoshka2 $fkaoshka
							lset fkaosdata $fkaoshkidx1 6 $fkaoshka
							lset fkaosdata $fkaoshkidx2 6 $fkaoshka
						}
					}
				}
			}
		}
	}
	set pre "NEW"
	set fkaosdbid [open $_rest$pre a+]
	foreach fkaoshkrec $fkaosdata {
		if { [lindex $fkaoshkrec 0] == "-" } {
			continue
		} else {
			puts $fkaosdbid $fkaoshkrec
		}
	}
	close $fkaosdbid
	file delete $_rest
	file rename $_rest$pre $_rest
}
alias fkaosset {
	global fkaosgrab
	global fkaosanswer
	global fkaosbot
	global fkaoschan
	fkaosreadconf
	if { [string equal $fkaosanswer "1"] } {
		print "fkaos : Grabbing is 	[bold][color 9]ON"
	} else {
		print "fkaos : Answering is [bold][color 5]OFF"
	}
	if { [string equal $fkaosgrab "1"] } {
		print "fkaos : Grabbing is 	[bold][color 9]ON"
	} else {
		print "fkaos : Grabbing is 	[bold][color 5]OFF"
	}
	print "fkaos : botnick : 	$fkaosbot"
	print "fkaos : chan : 		$fkaoschan"
}
alias grabfkaos {
	global fkaosgrab
	fkaosreadconf
	if { [string equal $fkaosgrab "1"] } {
		set fkaosgrab "0"
		print "fkaos : Grabbing is [bold][color 5]OFF"
	} else {
		set fkaosgrab "1"
		print "fkaos : Grabbing is [bold][color 9]ON"
	}
	fkaoswriteconf
}
alias answerfkaos {
	global fkaosanswer
	fkaosreadconf
	if { [string equal $fkaosanswer "1"] } {
		set fkaosanswer "0"
		print "fkaos : Answering is [bold][color 5]OFF"
	} else {
		set fkaosanswer "1"
		print "fkaos : Answering is [bold][color 9]ON"
	}
	fkaoswriteconf
}
